#input_type_name: ApplyReassignmentInput
#output_type_name: ApplyReassignmentResult
#function_name: apply_reassignment

"""Commit a recovery: reassign the pro, bump their load, notify the customer.

Side-effecting writer node for the recover-booking workflow. Composes the
customer message and records the audit trail in recovery_log.
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel


class ApplyReassignmentInput(BaseModel):
    booking_id: str
    pro_id: str
    pro_name: str
    eta_minutes: int = 0


class ApplyReassignmentResult(BaseModel):
    ok: bool
    booking_id: str
    pro_name: str
    customer_message: str
    status: str


def _compose_message(customer: str, service: str, pro_name: str, eta: int) -> str:
    return (
        f"Hi {customer}, your {service} is confirmed. Your original professional "
        f"became unavailable, so we've arranged {pro_name} to arrive in about "
        f"{eta} minutes. Reply here if that doesn't work for you. — YesMadam"
    )


async def apply_reassignment(
    ctx: FunctionContext, data: ApplyReassignmentInput
) -> ApplyReassignmentResult:
    pod = Pod.from_env()
    booking = pod.table("bookings").get(data.booking_id) or {}
    customer = booking.get("customer_name", "there")
    service = booking.get("service", "appointment")

    # Reassign the booking to the new professional.
    pod.table("bookings").update(
        data.booking_id,
        {"assigned_pro_id": data.pro_id, "status": "reassigned"},
    )

    # Bump the new pro's daily load.
    pro = pod.table("beauticians").get(data.pro_id) or {}
    pod.table("beauticians").update(
        data.pro_id, {"jobs_today": (pro.get("jobs_today") or 0) + 1}
    )

    message = _compose_message(customer, service, data.pro_name, data.eta_minutes)

    pod.table("recovery_log").create(
        {
            "booking_id": data.booking_id,
            "event": "reassigned",
            "actor": "agent",
            "detail": f"Reassigned to {data.pro_name} (ETA ~{data.eta_minutes} min).",
            "payload": {"pro_id": data.pro_id, "eta_minutes": data.eta_minutes},
        }
    )
    pod.table("recovery_log").create(
        {
            "booking_id": data.booking_id,
            "event": "customer_notified",
            "actor": "agent",
            "detail": message,
            "payload": {"channel": "telegram"},
        }
    )

    return ApplyReassignmentResult(
        ok=True,
        booking_id=data.booking_id,
        pro_name=data.pro_name,
        customer_message=message,
        status="reassigned",
    )
