#input_type_name: RiskScanInput
#output_type_name: RiskScanResult
#function_name: risk_scan

"""Proactive cancellation-risk radar.

For every upcoming booking, computes its "backup depth" — how many available,
qualified professionals could cover it if the assigned pro fell through. Bookings
with zero backups are the ones that WILL escalate, so this lets ops act before a
cancellation ever happens. This is what makes the system self-healing, not just
reactive.
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel


class RiskScanInput(BaseModel):
    only_open: bool = True  # only scheduled / at_risk bookings


class BookingRisk(BaseModel):
    booking_id: str
    customer_name: str
    service: str
    area: str | None = None
    skill_required: str | None = None
    price: float = 0.0
    backup_depth: int
    tier: str  # critical | at_risk | resilient


class RiskScanResult(BaseModel):
    scanned: int
    critical: int
    at_risk: int
    resilient: int
    revenue_at_risk: float  # ₹ of bookings with zero backups
    bookings: list[BookingRisk]


def _tier(depth: int) -> str:
    if depth == 0:
        return "critical"
    if depth <= 2:
        return "at_risk"
    return "resilient"


async def risk_scan(ctx: FunctionContext, data: RiskScanInput) -> RiskScanResult:
    pod = Pod.from_env()
    bookings = pod.query("SELECT * FROM bookings").to_dict()["items"]
    pros = pod.query(
        "SELECT * FROM beauticians WHERE status = 'active' AND is_available = true"
    ).to_dict()["items"]

    open_states = {"scheduled", "at_risk"}
    out: list[BookingRisk] = []
    crit = atr = res = 0
    rev_at_risk = 0.0

    for b in bookings:
        if data.only_open and b.get("status") not in open_states:
            continue
        skill = b.get("skill_required")
        depth = 0
        for p in pros:
            if skill and skill not in (p.get("skills") or []):
                continue
            jt, mx = p.get("jobs_today") or 0, p.get("max_jobs_per_day") or 0
            if mx and jt >= mx:
                continue
            depth += 1
        tier = _tier(depth)
        if tier == "critical":
            crit += 1
            rev_at_risk += float(b.get("price") or 0)
        elif tier == "at_risk":
            atr += 1
        else:
            res += 1
        out.append(BookingRisk(
            booking_id=b["id"], customer_name=b.get("customer_name", ""),
            service=b.get("service", ""), area=b.get("area"),
            skill_required=skill, price=float(b.get("price") or 0),
            backup_depth=depth, tier=tier))

    out.sort(key=lambda r: r.backup_depth)
    return RiskScanResult(
        scanned=len(out), critical=crit, at_risk=atr, resilient=res,
        revenue_at_risk=round(rev_at_risk, 2), bookings=out)
