# Submission Answers — copy/paste into Unstop

---

## Problem statement (short)

At-home services live or die in the 30 minutes before an appointment. When a
professional cancels last-minute, a human in ops has to drop everything, phone
around for a replacement, and calm the customer down — all at once. Most of the
time the slot is lost, the customer churns, and the goodwill refund is a guess.
Everyone has automated *booking*. Nobody has automated the *panic*.

---

## Product (what I built and how it solves it)

**Self-Healing Operations** — an AI operations agent that runs the recovery floor
end-to-end and only interrupts a human to spend money.

The moment a booking is at risk, my agent ranks every available professional by
skill, proximity, rating and current load, reassigns the best one, and messages
the customer — in under a second instead of eleven minutes. It doesn't just react,
either: a live **Risk Radar** scores every booking's *backup depth* (how many
qualified pros could cover it) and flags the ones that will break **before they
do** — that's what makes it self-healing.

And here's the product decision the whole thing is built around: the agent moves
fast on logistics, but it **never spends money on its own**. Every discount or
refund is computed from an explicit policy and queued for a human's one-tap
approval, with a full audit trail. **Automate the scramble, gate the spend.**

I deliberately built it on YesMadam's real operations problem, so it works as a
drop-in for an actual at-home-services business — not a toy.

---

## How I used the Lemma SDK

I built the entire product on Lemma — it's the infrastructure layer end to end:

- **Tables** — `bookings`, `beauticians`, plus `recovery_log` (a complete audit
  trail) and `comp_ledger` (the money gate), with foreign keys and typed enums.
- **Functions (9, Python)** — the brains: `risk_scan` (proactive radar),
  `match_pro` (the ranking engine, with haversine proximity), `recommend_comp`
  (the policy engine), `run_recovery` (one-click orchestration), `decide_comp`,
  plus the workflow writers and a `reset_demo` helper.
- **Workflow** — `recover-booking`, an 11-node graph that runs match → reassign →
  recommend, then **pauses on a native human-approval FORM** before settling, and
  branches to an escalation path when no pro is available.
- **Agent** — `ops-agent`, a conversational operations assistant with scoped
  permissions that can read the live data over SQL, run a recovery, and surface
  comps for approval — but is wired so money decisions stay with the human.
- **App** — `ops-board`, a single-file operator command center (impact KPIs, the
  Risk Radar, the approval queue and the recovery timeline), deployed on Lemma and
  talking to the pod live through the Lemma browser SDK.
- **Surface** — a **Telegram** surface on the agent, so the whole operation can be
  run from chat.

---

## External tools / models / APIs

I kept the stack intentionally lean — almost everything runs natively on Lemma:

- **Lemma SDK + hosted cloud** — data, functions, workflow, agent and app hosting.
  Model execution is provided by Lemma's runtime, so there's no separate model API
  key to manage.
- **Telegram** — via Lemma's built-in surface, for chat-based ops.
- **Python** for all functions; a no-build **HTML/JavaScript** single-file app for
  the dashboard.
- **Haversine** geo-distance scoring — implemented from scratch in the matching
  engine; no external maps API needed.

That self-contained footprint is deliberate: the whole system is reproducible from
one repo and one `lemma pods import`.
