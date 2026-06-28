# Demo Runbook — Self-Healing Operations

Pod: `ops-recovery` · Org: Rithick's Space · App: https://ops-board.apps.lemma.work

## 0. Setup (every terminal session, Windows PowerShell)

```powershell
$env:Path="C:\Users\rithi\.local\bin;$env:Path"
$env:PYTHONPATH="C:\Users\rithi\lemma-hackathon\scripts\winshim"
$env:PYTHONIOENCODING="utf-8"
# Fill these from your own workspace:
#   org id  ->  lemma orgs list --json
#   pod id  ->  lemma pod list --json   (pod name: ops-recovery)
$env:LEMMA_ORG_ID="<YOUR_ORG_ID>"
$pod="<YOUR_POD_ID>"
```

## 1. Reset to a clean state (before any demo)

```powershell
lemma --pod $pod function run reset_demo --data '{"confirm":true}'
```

---

## 2. Main demo — the operator App (~90 sec)

Open **https://ops-board.apps.lemma.work** (sign in with your Lemma account).

1. **The board** — 8 bookings today, all green. Point out the KPI tiles.
2. **Trigger a cancellation** — on **Pooja Hegde** (Facial, Jayanagar), click
   **"Cancel → recover."** Watch: status flips to *reassigned*, the timeline fills
   (detected → reassigned → customer notified), and a **₹120 discount appears in
   the Approval queue**.
3. **The human gate** — in the Approval queue, click **Approve**. The comp flips to
   *issued*, "Comp issued" KPI updates, timeline logs *comp_approved by operator*.
4. **Escalation** — on **Sara Ali** (Bridal, Whitefield), click
   **"Cancel → recover."** No bridal pro is free → booking **escalated**, a
   **₹5,000 refund** lands in the approval queue. Approve or reject it.
5. **Reset** — click **↺ Reset demo** to restore the clean state.

**The story:** the agent did all the logistics instantly; the only thing it asked
a human for was permission to spend money.

---

## 3. Showcase — the Lemma-native workflow with a human approval FORM

Shows the same recovery as an approval-gated Lemma workflow.

```powershell
# Get a booking id (e.g. Pooja Hegde)
lemma --pod $pod records list bookings --json | python C:\Users\rithi\lemma-hackathon\scripts\show_ids.py

# Run the workflow — it executes match -> reassign -> recommend, then PAUSES
lemma --pod $pod workflow run recover-booking --data '{"booking_id":"<POOJA_ID>"}'
# Status: WAITING, current node: approve  (wait_type HUMAN)

# Approve the recommended comp -> the run completes (settle -> issued)
lemma --pod $pod workflow runs submit-form <RUN_ID> --data '{"approved":true}'
```

For a no-match booking (Sara), the same workflow routes to **escalate**.

---

## 4. Showcase — the conversational ops-agent

```powershell
lemma --pod $pod agent run ops-agent "How many bookings today, and is anything escalated?"
lemma --pod $pod agent run ops-agent "Pooja Hegde's facial pro just cancelled. Recover it and summarise."
lemma --pod $pod agent run ops-agent "How much compensation have we issued today?"
```

The agent reads live SQL, runs recovery, and **surfaces comps for approval**
rather than issuing them.

---

## 5. Telegram — run the whole operation from chat

The ops-agent is wired to Telegram via **Lemma's built-in bot** (no BotFather token
needed). The surface is created with:

```powershell
'{ "mode": "DM" }' | Out-File -Encoding ascii tg.json
lemma --pod $pod surface upsert TELEGRAM --agent ops-agent --credential-mode SYSTEM --enabled -f tg.json
lemma --pod $pod surface setup TELEGRAM     # shows status: ACTIVE / Ready: yes
```

To link your own Telegram and chat with it, open the **Lemma dashboard** for this
pod → **Surfaces → Telegram → Open in Telegram**, then message the bot, e.g.:

- *"What's escalated right now?"*
- *"Pooja Hegde's pro cancelled — recover it."*
- *"How much comp have we issued today?"*

For a **customer-managed bot** instead (your own @BotFather token), connect it as a
connector account and pass `--credential-mode CUSTOM --account <account-id>`.
