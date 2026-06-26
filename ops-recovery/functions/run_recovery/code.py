#input_type_name: RunRecoveryInput
#output_type_name: RunRecoveryResult
#function_name: run_recovery

"""One-click recovery orchestrator for the operator app.

Self-contained: detect -> match -> reassign + notify -> recommend comp (queued
as PENDING for human approval), or escalate when no pro is available. Mirrors
the recover-booking workflow but in a single call the app can trigger, leaving
the comp_ledger 'pending' row as the human approval gate.
"""

from math import asin, cos, radians, sin, sqrt

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel

_ETA_BASE_MIN = 15.0
_ETA_MIN_PER_KM = 3.0
_GRACE_MIN = 15
_MINOR_MAX_MIN = 30
_PCT_MINOR = 0.10
_PCT_MAJOR = 0.20


class RunRecoveryInput(BaseModel):
    booking_id: str


class RunRecoveryResult(BaseModel):
    ok: bool
    outcome: str  # recovered | awaiting_approval | escalated | error
    booking_id: str
    pro_name: str | None = None
    eta_minutes: int | None = None
    comp_type: str = "none"
    comp_amount: float = 0.0
    customer_message: str | None = None
    detail: str = ""


def _haversine_km(lat1, lng1, lat2, lng2):
    if None in (lat1, lng1, lat2, lng2):
        return 8.0
    r = 6371.0
    d_lat, d_lng = radians(lat2 - lat1), radians(lng2 - lng1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    return round(2 * r * asin(sqrt(a)), 2)


def _log(pod, booking_id, event, detail, actor="agent", payload=None):
    pod.table("recovery_log").create(
        {"booking_id": booking_id, "event": event, "actor": actor,
         "detail": detail, "payload": payload or {}}
    )


async def run_recovery(ctx: FunctionContext, data: RunRecoveryInput) -> RunRecoveryResult:
    pod = Pod.from_env()
    booking = pod.table("bookings").get(data.booking_id)
    if not booking:
        return RunRecoveryResult(ok=False, outcome="error", booking_id=data.booking_id,
                                 detail="Booking not found.")

    pod.table("bookings").update(data.booking_id, {"status": "at_risk"})
    _log(pod, data.booking_id, "detected", "Original professional became unavailable.")

    skill = booking.get("skill_required")
    price = float(booking.get("price") or 0.0)
    customer = booking.get("customer_name", "there")
    service = booking.get("service", "appointment")

    rows = pod.query(
        "SELECT * FROM beauticians WHERE status = 'active' AND is_available = true"
    ).to_dict()["items"]

    best, best_score, best_eta = None, -1.0, 0
    for pro in rows:
        if skill and skill not in (pro.get("skills") or []):
            continue
        jt, mx = pro.get("jobs_today") or 0, pro.get("max_jobs_per_day") or 0
        if mx and jt >= mx:
            continue
        dist = _haversine_km(booking.get("lat"), booking.get("lng"), pro.get("lat"), pro.get("lng"))
        score = 1.0 / (1.0 + dist) + (pro.get("rating") or 0) / 5.0 * 0.6
        if score > best_score:
            best, best_score = pro, score
            best_eta = int(round(_ETA_BASE_MIN + _ETA_MIN_PER_KM * dist))

    # --- No match: escalate with a full refund queued for approval ---
    if not best:
        pod.table("bookings").update(data.booking_id, {"status": "escalated"})
        pod.table("comp_ledger").create(
            {"booking_id": data.booking_id, "type": "refund", "amount": price,
             "reason": f"No available {skill} professional for {customer}.",
             "recommended_by": "run_recovery", "status": "pending"}
        )
        _log(pod, data.booking_id, "escalated",
             f"No replacement found. Full refund ({price:.0f} INR) queued for approval.")
        return RunRecoveryResult(
            ok=True, outcome="escalated", booking_id=data.booking_id,
            comp_type="refund", comp_amount=price,
            detail=f"Escalated — {price:.0f} INR refund pending approval.")

    # --- Match: reassign + notify the customer ---
    pod.table("bookings").update(
        data.booking_id, {"assigned_pro_id": best["id"], "status": "reassigned"})
    pod.table("beauticians").update(best["id"], {"jobs_today": (best.get("jobs_today") or 0) + 1})
    message = (
        f"Hi {customer}, your {service} is confirmed. Your original professional "
        f"became unavailable, so we've arranged {best['name']} to arrive in about "
        f"{best_eta} minutes. Reply here if that doesn't work. — YesMadam")
    _log(pod, data.booking_id, "reassigned",
         f"Reassigned to {best['name']} (ETA ~{best_eta} min).",
         payload={"pro_id": best["id"], "eta_minutes": best_eta})
    _log(pod, data.booking_id, "customer_notified", message, payload={"channel": "telegram"})

    # --- Comp policy ---
    if best_eta <= _GRACE_MIN:
        _log(pod, data.booking_id, "resolved", "Recovered within grace window — no comp needed.")
        return RunRecoveryResult(
            ok=True, outcome="recovered", booking_id=data.booking_id,
            pro_name=best["name"], eta_minutes=best_eta, customer_message=message,
            detail="Recovered within grace window — no compensation needed.")

    pct = _PCT_MINOR if best_eta <= _MINOR_MAX_MIN else _PCT_MAJOR
    amount = round(price * pct, 2)
    reason = f"~{best_eta}-min delay — {int(pct * 100)}% goodwill discount."
    pod.table("comp_ledger").create(
        {"booking_id": data.booking_id, "type": "discount", "amount": amount,
         "reason": reason, "recommended_by": "run_recovery", "status": "pending"})
    _log(pod, data.booking_id, "comp_recommended", reason)
    return RunRecoveryResult(
        ok=True, outcome="awaiting_approval", booking_id=data.booking_id,
        pro_name=best["name"], eta_minutes=best_eta, comp_type="discount",
        comp_amount=amount, customer_message=message,
        detail=f"Reassigned to {best['name']}; {amount:.0f} INR discount pending approval.")
