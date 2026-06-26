# Self-Healing Operations — Submission

**Gappy AI "Ship to Get Hired" Hackathon · Built on the Lemma SDK**
Target domain & hiring partner: **YesMadam** (at-home beauty & wellness)

> **One line:** An AI operations agent that runs the recovery floor for an
> at-home services business end-to-end — and only interrupts a human when it
> wants to spend money.

---

## 1. The problem

**User:** the City Operations Lead at an at-home services company (YesMadam).

**The painful moment:** a service professional cancels or no-shows **30–60 minutes
before** a booked appointment. Today a human scrambles to phone around for a
replacement while the customer sits in the dark. The slot is often lost, the
customer churns, and refund/goodwill decisions are made ad-hoc and inconsistently.

**Cost per incident:** lost booking revenue + an idle paid professional elsewhere
+ a churned customer (LTV) + inconsistent goodwill spend.

## 2. The product

**It is proactive, not just reactive.** A live **Risk Radar** scores every booking's
*backup depth* — how many qualified, available pros could cover it — and flags
**critical gaps before any cancellation happens** (e.g. a Bridal Makeup booking with
zero free specialists = ₹5,000 of revenue one cancellation away from being lost).
That is what makes it *self-healing*, not just recovery.

When a booking does go at risk, the system:

1. **Detects** the gap (booking → `at_risk`).
2. **Recovers** — ranks every available professional by **skill + proximity
   (haversine) + rating + spare capacity**, reassigns the best one, updates the
   schedule.
3. **Communicates** — composes and sends the customer a clear message
   (Telegram surface; logged to the audit trail).
4. **Gates the spend** — if the recovery warrants goodwill compensation, the
   amount is computed from a written policy and **queued for human approval**.
   A human approves or rejects; nothing is issued silently.
5. **Records** everything as structured rows — a complete, queryable audit trail.

**The sharp product call:** *automate the scramble, gate the spend.* The agent
moves fast on logistics (which is safe to automate) but **money decisions always
require a human** — the single most important judgment in this domain.

## 3. How it's built on Lemma

| Lemma primitive | Used for |
|---|---|
| **Tables** (4) | `bookings`, `beauticians`, `recovery_log` (audit), `comp_ledger` (the money gate) — typed, with foreign keys & enums |
| **Functions** (9, Python) | `risk_scan` (proactive radar), `match_pro` (ranking engine), `recommend_comp` (policy engine), `apply_reassignment`, `settle_comp`, `escalate_booking`, `run_recovery` (one-click orchestrator), `decide_comp`, `reset_demo` |
| **Workflow** (`recover-booking`) | 11-node graph: `match → DECISION → reassign → recommend → DECISION → ` **`FORM (human approval)`** ` → settle / escalate`. JMESPath routing, native human-in-the-loop approval form |
| **Agent** (`ops-agent`) | Conversational operations assistant — answers questions over the data *and* triggers recovery / applies approved comps, with scoped grants |
| **App** (`ops-board`) | Live operations command center: **impact hero** (coverage %, ₹ revenue shielded, critical gaps, comp issued), **Risk Radar**, **approval queue**, recovery timeline, and a one-click **"Simulate the full day"** — deployed at `https://ops-board.apps.lemma.work` |
| **Files** | `comp-policy.md` — the human-readable source of truth the `recommend_comp` function enforces |

Two front doors over the **same** logic: a visual **operator App** and a
**conversational agent** — plus a Lemma-native **workflow** that expresses the
exact same recovery as an approval-gated graph.

## 4. Demo scenarios (seeded, deterministic)

- **Recovery + approval** — *Pooja Hegde, Facial, Jayanagar.* Nearest available
  Facial pro is **Aarti Sharma** (~3.5 km). Reassigned, customer notified, and a
  **₹120 (10%) discount queued for approval** → operator approves → issued.
- **Escalation** — *Sara Ali, Bridal Makeup, Whitefield.* Both bridal-skilled pros
  are off → **no match** → booking escalated, **₹5,000 full refund queued for
  approval**.
- **Fast path** — *Riya Kapoor, Facial, Koramangala.* Replacement is on the spot
  (within the 15-min grace window) → recovered with **no compensation**.

## 5. Compensation policy (enforced by `recommend_comp`)

| Situation | Comp | Approval |
|---|---|---|
| Replacement within 15 min | none | — |
| 15–30 min delay | 10% discount | required |
| >30 min or downgrade | 20% discount | required |
| No replacement (escalation) | 100% refund + credit | required |

## 6. Why this fits the rubric

- **Problem clarity & real-world fit (35%)** — one user, one sharply-defined
  painful moment, quantified cost, in a hiring partner's exact domain.
- **Product judgment (25%)** — automate logistics, gate money; the agent
  *recommends*, the human *decides*; policy is explicit and auditable.
- **Execution quality (25%)** — every path tested live on the cloud; complete
  audit trail; clean, deployed operator app; zero pod-doctor errors.
- **Lemma utilization (15%)** — tables, functions, a multi-node workflow with a
  **native human-approval form**, a scoped agent, an app, and a policy file.

## 7. Hiring relevance

This is, deliberately, a working slice of **YesMadam's** real operations problem.
The submission doubles as a job audition: it demonstrates AI product engineering
(orchestration, ranking, approval-gated automation) and product judgment
(knowing exactly where the human belongs).

## 8. Notes

- Runs entirely on Lemma's **hosted cloud** — models execute out of the box (no
  external API key needed).
- Built on **Windows**; the SDK CLI (v0.5.0) needed a small `termios`/`tty` shim
  to run on Windows (see `scripts/winshim/`).
