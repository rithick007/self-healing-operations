#input_type_name: EscalateBookingInput
#output_type_name: EscalateBookingResult
#function_name: escalate_booking

"""Escalate a booking that could not be auto-recovered.

Marks the booking escalated, queues a full-refund comp for human approval,
and logs the audit trail. This is the no-match branch of the workflow.
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel


class EscalateBookingInput(BaseModel):
    booking_id: str
    reason: str = "No available professional could be found."


class EscalateBookingResult(BaseModel):
    ok: bool
    booking_id: str
    refund_amount: float
    detail: str


async def escalate_booking(
    ctx: FunctionContext, data: EscalateBookingInput
) -> EscalateBookingResult:
    pod = Pod.from_env()
    booking = pod.table("bookings").get(data.booking_id) or {}
    price = float(booking.get("price") or 0.0)
    customer = booking.get("customer_name", "the customer")

    pod.table("bookings").update(data.booking_id, {"status": "escalated"})

    pod.table("comp_ledger").create(
        {
            "booking_id": data.booking_id,
            "type": "refund",
            "amount": price,
            "reason": f"No replacement for {customer}: {data.reason}",
            "recommended_by": "escalate_booking",
            "status": "pending",
        }
    )
    pod.table("recovery_log").create(
        {
            "booking_id": data.booking_id,
            "event": "escalated",
            "actor": "agent",
            "detail": f"Escalated to ops — {data.reason} Full refund ({price:.0f} INR) queued for approval.",
            "payload": {"reason": data.reason, "refund": price},
        }
    )
    return EscalateBookingResult(
        ok=True,
        booking_id=data.booking_id,
        refund_amount=price,
        detail=f"Escalated; {price:.0f} INR refund pending approval.",
    )
