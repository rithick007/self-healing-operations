# Compensation Policy — At-Home Services Recovery

> Source of truth for goodwill comp on disrupted bookings. The `recommend_comp`
> function enforces these rules deterministically; a human operator approves
> every non-zero comp before it is issued (the `comp_ledger` gate).

## Principle

Automate the *scramble*, gate the *spend*. The agent may reassign pros and
message customers on its own, but **money decisions always need human sign-off.**

## Rules

| Situation | Comp | Amount | Approval |
|---|---|---|---|
| Replacement arrives within **15 min** of the original slot | none | ₹0 | not required |
| Replacement delayed **15–30 min** | discount | **10%** of booking price | required |
| Replacement delayed **>30 min**, or a service downgrade | discount | **20%** of booking price | required |
| **No replacement** available (escalation) | refund | **100%** of booking price + apology credit | required |

## Notes

- ETA/delay is estimated by `match_pro` from travel distance (`15 min base + 3 min/km`).
- Approval queue surfaces in the operator App and via `lemma workflow runs waiting`.
- Every recommendation and decision is written to `recovery_log` and `comp_ledger`
  for a complete audit trail.
