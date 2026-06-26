# Self-Healing Operations

> An AI operations agent that recovers at-risk at-home-service bookings end-to-end
> — and only interrupts a human to spend money.
>
> Built on the **Lemma SDK** for the Gappy AI "Ship to Get Hired" hackathon.
> Target domain / hiring partner: **YesMadam**.

**Live operator app:** https://ops-board.apps.lemma.work

## What it does

When a professional cancels minutes before an appointment, the system detects the
gap, ranks and reassigns the best available pro (skill + proximity + rating +
load), messages the customer, and — only when goodwill compensation is warranted —
**queues it for human approval**. No replacement available → it escalates with a
refund queued. Every step lands as a structured, auditable row.

## Repo layout

```
ops-recovery/        Lemma pod bundle (source of truth, imported with `lemma pods import`)
  tables/            bookings, beauticians, recovery_log, comp_ledger
  functions/         match_pro, recommend_comp, apply_reassignment, settle_comp,
                     escalate_booking, run_recovery, decide_comp, reset_demo
  workflows/         recover-booking (match -> approve(FORM) -> settle / escalate)
  agents/            ops-agent (conversational operations assistant)
app/ops-board/       single-file operator dashboard (deployed app)
data/                seed datasets (Bangalore: 10 pros, 8 bookings)
scripts/             helpers + winshim/ (Windows termios/tty shim for the CLI)
docs/                SUBMISSION.md, DEMO.md, architecture.md, comp-policy.md
```

## Read next

- **docs/SUBMISSION.md** — the writeup (problem, product, architecture, rubric).
- **docs/DEMO.md** — step-by-step demo runbook.
- **docs/architecture.md** — full design spec.

## Notes

Runs on Lemma's hosted cloud (models included; no external key needed). The CLI
needed a small `termios`/`tty` shim to run on Windows — see `scripts/winshim/`.
