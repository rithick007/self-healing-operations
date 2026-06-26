#input_type_name: DecideCompInput
#output_type_name: DecideCompResult
#function_name: decide_comp

"""Operator decision on a pending compensation (the human approval gate).

Called from the operator app's Approve / Reject buttons. Flips the
comp_ledger row to issued or rejected and records the audit trail.
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel


class DecideCompInput(BaseModel):
    comp_id: str
    approved: bool
    decided_by: str = "operator"


class DecideCompResult(BaseModel):
    ok: bool
    comp_id: str
    status: str
    detail: str


async def decide_comp(ctx: FunctionContext, data: DecideCompInput) -> DecideCompResult:
    pod = Pod.from_env()
    comp = pod.table("comp_ledger").get(data.comp_id)
    if not comp:
        return DecideCompResult(ok=False, comp_id=data.comp_id, status="error",
                                detail="Comp not found.")

    status = "issued" if data.approved else "rejected"
    pod.table("comp_ledger").update(
        data.comp_id, {"status": status, "decided_by": data.decided_by})

    amount = float(comp.get("amount") or 0)
    ctype = comp.get("type", "comp")
    verb = "issued" if data.approved else "rejected"
    detail = f"{ctype.title()} of {amount:.0f} INR {verb} by {data.decided_by}."
    pod.table("recovery_log").create(
        {"booking_id": comp.get("booking_id"),
         "event": "comp_approved" if data.approved else "comp_rejected",
         "actor": "human", "detail": detail,
         "payload": {"comp_id": data.comp_id, "type": ctype, "amount": amount}})

    return DecideCompResult(ok=True, comp_id=data.comp_id, status=status, detail=detail)
