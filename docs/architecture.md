# Self-Healing Operations — Architecture & Build Spec

> Gappy AI "Ship to Get Hired" Hackathon · Lemma SDK · target partner: **YesMadam**
> Submit by **2026-06-30**.

## 1. Problem (the 35% bucket — keep this razor-sharp)

**User:** City Operations Lead at an at-home services company (YesMadam).

**The painful moment:** A service pro (beautician) cancels or no-shows **30–60 minutes before** a booked appointment. Today a human ops person manually phones around for a replacement, the customer is left in the dark, the slot is often lost, the customer churns, and refund/comp decisions are ad-hoc and inconsistent.

**Cost per incident:** lost booking revenue + an idle paid pro elsewhere + a churned customer (LTV) + inconsistent goodwill spend.

**The product, in one line:** *An AI ops agent that runs the recovery floor end-to-end and only interrupts a human when it wants to spend money.*

## 2. The core loop (the demoable spine)

1. **Detect** — a cancellation flips a `bookings` row to `at_risk` (DATASTORE_EVENT trigger).
2. **Recover** — agent/function queries `beauticians` for nearby, available, skill-matched pros; ranks them; reassigns the best; updates the schedule.
3. **Communicate** — agent messages the customer on a **Surface** (Telegram for demo; WhatsApp = production target).
4. **Approve (the human gate)** — if recovery needs a comp/discount/refund, the workflow **pauses for human sign-off**, showing the agent's *recommended* comp derived from the markdown **comp-policy** playbook. One tap → agent executes + messages the customer.
5. **Record** — every step lands as structured rows (`recovery_log`, `comp_ledger`); an operator **App** shows the live ops board.

**The sharp product call:** automate the *scramble* (speed), gate the *spend* (money). That single decision is the product-judgment story (25% bucket).

## 3. Data model (Lemma tables)

> Auto columns `id, created_at, updated_at, user_id` are added by Lemma — never declared.

### `bookings`
| column | type | notes |
|---|---|---|
| customer_name | TEXT (required) | |
| customer_phone | TEXT (required) | demo: Telegram chat id |
| service | TEXT (required) | e.g. "Haircut at Home" |
| skill_required | TEXT (required) | matches a `beauticians.skills` entry |
| city | TEXT | |
| area | TEXT | locality for proximity |
| lat | FLOAT | |
| lng | FLOAT | |
| scheduled_at | DATETIME (required) | |
| duration_min | INTEGER | |
| price | FLOAT | |
| original_pro_id | UUID | FK beauticians.id |
| assigned_pro_id | UUID | FK beauticians.id (nullable) |
| status | ENUM | scheduled, at_risk, recovering, reassigned, escalated, completed, cancelled |
| notes | TEXT | |

### `beauticians`
| column | type | notes |
|---|---|---|
| name | TEXT (required) | |
| phone | TEXT | |
| skills | JSON | array, e.g. ["Haircut","Facial"] |
| city | TEXT | |
| area | TEXT | |
| lat | FLOAT | |
| lng | FLOAT | |
| rating | FLOAT | 0–5 |
| is_available | BOOLEAN | |
| jobs_today | INTEGER | for load balancing |
| max_jobs_per_day | INTEGER | |
| status | ENUM | active, off, busy |

### `recovery_log` (audit trail)
| column | type | notes |
|---|---|---|
| booking_id | UUID | FK bookings.id |
| event | ENUM | detected, matched, reassigned, customer_notified, comp_recommended, comp_approved, comp_rejected, escalated, resolved, failed |
| actor | ENUM | agent, human, system |
| detail | TEXT | human-readable line |
| payload | JSON | structured context |

### `comp_ledger` (the money gate)
| column | type | notes |
|---|---|---|
| booking_id | UUID | FK bookings.id |
| type | ENUM | discount, refund, credit, free_addon, none |
| amount | FLOAT | |
| reason | TEXT | |
| recommended_by | TEXT | agent name |
| status | ENUM | pending, approved, rejected, issued |
| decided_by | TEXT | human |

## 4. Logic, agents & workflow

- **File:** `comp-policy.md` — markdown playbook the agent reads to *recommend* (not decide) a comp. e.g. delay 15–30m → 10% off; >30m or downgrade → 20% off or free add-on; no recovery → full refund + credit.
- **Function `match_pro` (API):** deterministic ranking — filter `beauticians` by skill + availability + same area/city, score by `proximity, rating, load`, return best candidate or `null`.
- **Function `recommend_comp` (API):** reads policy + delay/downgrade facts → proposes comp type+amount.
- **Agent `recovery-agent`:** orchestrates messaging + reasoning; toolsets `POD` (+ surface). Grants: read `beauticians`, read/write `bookings`, `recovery_log`, `comp_ledger`.
- **Workflow `recover-booking`** (start: DATASTORE_EVENT on `bookings.status == at_risk`):
  `detect → match_pro (FUNCTION) → DECISION match? → [yes] reassign + notify customer + recommend_comp → DECISION comp needed? → [yes] human APPROVAL → execute + notify → END · [no match] escalate to ops surface → END`
  - **Approval mechanism: TBD — verify in SDK** (candidates: a `FORM` node mid-workflow, `WAIT_UNTIL`, or a dedicated Approvals primitive). Confirm before building step 4.
- **Surface `telegram`:** `default_agent_name = recovery-agent` for customer + ops comms.
- **App:** single-file operator board — at-risk queue, live recoveries, pending comp approvals, CX timeline.

## 5. Lemma primitives used (the 15% bucket — we use nearly all)

Tables ✓ · Files/playbook ✓ · Functions ✓ · Agent ✓ · Workflow w/ DECISION + human approval ✓ · Surface (Telegram/WhatsApp) ✓ · App ✓ · Permissions/grants ✓ · (Schedule optional for the "predict at-risk" stretch goal)

## 6. Demo script (90 sec)

1. Show the live ops board: today's bookings, all green.
2. Trigger a cancellation (flip one booking → `at_risk`).
3. Watch the agent: match a new pro → reassign → Telegram message hits the customer's phone live.
4. A comp approval pops on the ops board → operator taps **Approve** → customer gets the discount message.
5. One booking has *no* available pro → agent escalates to the ops channel. Show the `recovery_log` + `comp_ledger` rows as the audit trail.

## 7. Rubric mapping

| Criterion | Weight | How we win it |
|---|---|---|
| Problem clarity & real-world fit | 35% | One user, one painful moment, quantified cost, partner-aligned (YesMadam) |
| Product judgment | 25% | Automate the scramble, gate the spend; agent *recommends*, human *decides* |
| Execution quality | 25% | Reliable end-to-end demo; structured audit trail; clean ops board |
| Lemma utilization | 15% | Uses tables, files, functions, agent, workflow+approval, surface, app |

## 8. Open items to verify after auth

- [ ] Exact project/import structure (`lemma import` vs `lemma <resource> apply`) and folder layout.
- [ ] Approval primitive semantics (how a workflow pauses for human sign-off).
- [x] Hosted cloud runs models out of the box — no model provider key needed.
- [ ] Telegram surface setup via `lemma connectors` (CUSTOM credential mode).
