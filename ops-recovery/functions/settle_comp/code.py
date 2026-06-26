#input_type_name: SettleCompInput
#output_type_name: SettleCompResult
#function_name: settle_comp

"""Persist a compensation decision to the comp_ledger and audit trail.

Called after the human approval form. Writes the final ledger row and logs
whether the comp was approved, rejected, or unnecessary.
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel


class SettleCompInput(BaseModel):
    booking_id: str
    approved: bool
    type: str = "none"
    amount: float = 0.0
    reason: str = ""
    decided_by: str = "operator"


class SettleCompResult(BaseModel):
    ok: bool
    booking_id: str
    ledger_status: str
    detail: str


async def settle_comp(ctx: FunctionContext, data: SettleCompInput) -> SettleCompResult:
    pod = Pod.from_env()

    if data.type == "none" or data.amount <= 0:
        pod.table("recovery_log").create(
            {
                "booking_id": data.booking_id,
                "event": "resolved",
                "actor": "agent",
                "detail": "Recovered within grace window — no compensation needed.",
            }
        )
        return SettleCompResult(
            ok=True,
            booking_id=data.booking_id,
            ledger_status="none",
            detail="No compensation required.",
        )

    ledger_status = "issued" if data.approved else "rejected"
    event = "comp_approved" if data.approved else "comp_rejected"
    verb = "issued" if data.approved else "rejected"

    pod.table("comp_ledger").create(
        {
            "booking_id": data.booking_id,
            "type": data.type,
            "amount": data.amount,
            "reason": data.reason or "Goodwill compensation for disrupted booking.",
            "recommended_by": "recommend_comp",
            "status": ledger_status,
            "decided_by": data.decided_by,
        }
    )
    detail = f"{data.type.title()} of {data.amount:.0f} INR {verb} by {data.decided_by}."
    pod.table("recovery_log").create(
        {
            "booking_id": data.booking_id,
            "event": event,
            "actor": "human",
            "detail": detail,
            "payload": {"type": data.type, "amount": data.amount},
        }
    )
    return SettleCompResult(
        ok=True, booking_id=data.booking_id, ledger_status=ledger_status, detail=detail
    )
