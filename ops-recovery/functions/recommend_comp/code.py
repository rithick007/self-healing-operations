#input_type_name: RecommendCompInput
#output_type_name: RecommendCompResult
#function_name: recommend_comp

"""Recommend a goodwill compensation for a disrupted booking.

Implements the rules documented in files/policy/comp-policy.md so the
recommendation is deterministic and auditable. The function only RECOMMENDS;
a human approves before anything is issued (the comp_ledger gate).
"""

from lemma_sdk import FunctionContext, Pod
from pydantic import BaseModel

_PCT_MINOR = 0.10  # 15-30 min delay
_PCT_MAJOR = 0.20  # >30 min delay or a service downgrade
_GRACE_MIN = 15
_MINOR_MAX_MIN = 30


class RecommendCompInput(BaseModel):
    booking_id: str
    recovered: bool
    eta_minutes: int = 0
    downgrade: bool = False


class RecommendCompResult(BaseModel):
    booking_id: str
    type: str  # discount | refund | credit | free_addon | none
    amount: float = 0.0
    currency: str = "INR"
    requires_approval: bool = False
    policy_rule: str
    reason: str


async def recommend_comp(ctx: FunctionContext, data: RecommendCompInput) -> RecommendCompResult:
    pod = Pod.from_env()
    booking = pod.table("bookings").get(data.booking_id)
    price = float((booking or {}).get("price") or 0.0)

    if not data.recovered:
        return RecommendCompResult(
            booking_id=data.booking_id,
            type="refund",
            amount=round(price, 2),
            requires_approval=True,
            policy_rule="no_recovery",
            reason="No replacement available — full refund plus an apology credit is recommended.",
        )

    if data.eta_minutes <= _GRACE_MIN and not data.downgrade:
        return RecommendCompResult(
            booking_id=data.booking_id,
            type="none",
            amount=0.0,
            requires_approval=False,
            policy_rule="within_grace",
            reason=f"Replacement arrives within the {_GRACE_MIN}-min grace window — no comp needed.",
        )

    if data.eta_minutes <= _MINOR_MAX_MIN and not data.downgrade:
        return RecommendCompResult(
            booking_id=data.booking_id,
            type="discount",
            amount=round(price * _PCT_MINOR, 2),
            requires_approval=True,
            policy_rule="minor_delay",
            reason=f"~{data.eta_minutes}-min delay — a {int(_PCT_MINOR * 100)}% goodwill discount is recommended.",
        )

    return RecommendCompResult(
        booking_id=data.booking_id,
        type="discount",
        amount=round(price * _PCT_MAJOR, 2),
        requires_approval=True,
        policy_rule="major_delay_or_downgrade",
        reason=(
            f"~{data.eta_minutes}-min delay"
            + (" with a service downgrade" if data.downgrade else "")
            + f" — a {int(_PCT_MAJOR * 100)}% discount is recommended."
        ),
    )
