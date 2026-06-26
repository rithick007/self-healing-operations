# Pitch & Demo Video Script (~90 seconds)

Record the screen at https://ops-board.apps.lemma.work. Reset the demo first.
Speak in a confident, founder voice. Beats below: **[ACTION]** + *spoken line*.

---

### Hook (0:00–0:12)
**[Show the command center, full board]**
> "Every day, at-home services like YesMadam lose bookings the moment a
> professional cancels last-minute. A human scrambles, the customer is left
> hanging, the slot dies. We built the agent that fixes this — automatically."

### The proactive twist (0:12–0:28)
**[Point at the Risk Radar — Sara Ali's bridal booking flagged 'no backup', critical]**
> "It's not just reactive. The Risk Radar scores every booking *before* anything
> breaks — here it's flagging a ₹5,000 bridal booking with zero qualified backups.
> That's revenue one cancellation away from gone. Coverage today: live, up top."

### The magic — one cancellation (0:28–0:50)
**[Click "Cancel → recover" on Pooja Hegde]**
> "Watch what happens when a pro cancels. The agent detects it, ranks every
> available professional by skill, distance and rating, reassigns the best one,
> and messages the customer — in under a second."
**[Timeline fills; ₹120 lands in the approval queue]**
> "And here's the judgment call: it does *not* spend money on its own. The goodwill
> discount goes to a human." **[Click Approve]** "Approve — issued, logged, done."

### The scale — whole day (0:50–1:08)
**[Click "Simulate the full day"; board lights up]**
> "Now the whole day at once. Eight bookings, handled in seconds — recovered where
> it can, escalated with a refund queued where no one's available. Look at the
> impact bar: manual dispatch is eleven minutes and forty percent lost slots.
> This is under ten seconds and near-total coverage."

### The agent (1:08–1:20) — optional
**[Telegram or `lemma agent run ops-agent "what's escalated?"`]**
> "Same brain, conversational. Ops can just ask — or the customer replies on
> WhatsApp and the agent handles it."

### Close (1:20–1:30)
**[Back to the impact hero]**
> "Built entirely on the Lemma SDK — structured data, functions, a workflow with a
> native human-approval step, an agent, and this app. It's a working slice of
> YesMadam's real operations. That's the team I want to build it with."

---

## One-liner (for the submission form)
> An AI operations agent that runs the recovery floor for at-home services
> end-to-end — predicts which bookings will break, auto-reassigns a new pro and
> notifies the customer in seconds, and only ever interrupts a human to spend
> money. Built on Lemma.

## Talking points if judges probe
- **Why it's defensible:** the human gate is on *spend*, not speed — the one place
  judgment matters. Policy is explicit and auditable (`comp_ledger` + `recovery_log`).
- **Why Lemma:** the whole thing is approval-gated ops automation — exactly what the
  SDK is for. We use tables, 9 functions, a multi-node workflow with a human-approval
  FORM, a scoped agent, and a deployed app.
- **What's next (project track):** real predictive risk (pro reliability history),
  live two-way customer negotiation, multi-city load balancing.
