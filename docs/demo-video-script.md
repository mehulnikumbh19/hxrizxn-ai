# Hxrizxn AI — Demo Video Script

**Target length:** 2:30–3:00. **Track:** Reasoning Agents.
**Goal:** prove it's *real* multi-step reasoning, grounded and honest, across business AND human decisions.

Format below: **[TIME] SHOT — what's on screen** / *what you say.*

---

## [0:00–0:20] HOOK — the problem

**SHOT:** Landing page, then a quick cut of a generic chatbot confidently answering "Yes, quit your job!"

> "Most AI tools answer instantly and confidently — even when they're guessing. For decisions you can't undo, that confidence is the danger. Hxrizxn is different: it *reasons* through your decision across futures, and it cites its evidence or admits what it can't know."

---

## [0:20–0:45] THE DECISION — set up the run

**SHOT:** Type a real decision into the intake. Use the **enterprise contract** prompt (clean, business, judge-friendly):
> *"Should we accept a $900k enterprise contract with heavy custom features that delays our roadmap 6 months and risks engineering burnout?"*

Fill goals (revenue, proof point) and fears (burnout, roadmap delay, customer concentration). Hit analyze.

> "I give it one hard, real decision — and eleven specialized agents go to work."

---

## [0:45–1:15] THE REASONING — the "Behind the scenes" trace

**SHOT:** The live agent trace panel. Let it populate. Point cursor down the list as agents complete with real latencies.

> "This isn't one prompt pretending to think. Eleven distinct reasoning agents run in sequence — framing the decision, grounding it in evidence, mining hidden assumptions, branching into optimistic, base, and stress futures, mapping ripple effects, weighing regret and reversibility, hunting black-swan risks. Each step is real, timed, and inspectable. You can watch the reasoning happen."

*(Linger on the real per-agent times — 7s, 12s, 20s — to show genuine model work, not instant fakery.)*

---

## [1:15–1:55] THE DIFFERENTIATOR — cite-or-abstain

**SHOT:** Navigate to **Ripple Effects** → scroll to the **Evidence & Honesty** panel. Point to a green **Grounded** badge, then an amber **Unverified** one.

> "Here's what makes it trustworthy. Every assumption and every risk is checked against the Foundry IQ knowledge base. When there's evidence, the agent grounds the claim and shows the source it cites. When there isn't, it marks the claim Unverified and *abstains* — it refuses to assert what it can't back up."

**SHOT:** Point specifically at the black-swan risk, still amber.

> "And notice — the black-swan risk stays unverified on purpose. Speculation is labeled as speculation. That's an anti-hallucination mechanism built into the reasoning itself."

---

## [1:55–2:25] THE RANGE — it reasons about human decisions too

**SHOT:** Quick new run with the **relationship** prompt. Jump to its Evidence & Honesty panel showing mostly green Grounded badges with relationship sources.

> "And it's not just business. The same engine reasons through deeply personal decisions — here, someone torn between two relationships. It surfaces emotional backlash, hidden resentment, isolation risk — grounded in relationship decision-science, with a Safety agent watching for genuine wellbeing risk. One engine: a contract and a heartbreak, both answered with evidence and humility."

---

## [2:25–2:50] THE PAYOFF — the memo + close

**SHOT:** The recommendation memo: bands not point estimates, citations, disclaimers.

> "It lands on a recommendation — but an honest one. Probability bands, not false precision. Cited evidence. Clear disclaimers. It's decision *support*, and it knows its limits."

**SHOT:** Architecture badge / "Live on Azure Container Apps" / the URL.

> "Built on Microsoft Foundry — Azure OpenAI for reasoning, Foundry IQ for grounding — and live on Azure right now. Hxrizxn: a second opinion for the decisions you can't take back."

**END CARD:** logo + live URL + "Solve for x, before life solves it for you."

---

## Shot checklist (capture these before editing)

- [ ] Landing page (3s)
- [ ] Intake filled with the enterprise prompt
- [ ] **Behind the scenes** trace populating with real latencies (the money shot)
- [ ] Evidence & Honesty panel — a Grounded badge + its citation, an Unverified badge
- [ ] Black-swan risk shown as Unverified
- [ ] Relationship run → its Evidence & Honesty panel (mostly Grounded)
- [ ] Recommendation memo with bands + disclaimers
- [ ] Architecture / Azure / live URL end card

## Production notes

- **Pre-run both decisions once** before recording so live model latency doesn't create dead air; if needed, speed-ramp the 20–60s analyze wait in editing.
- **Make sure the deployed site is in live mode and the Foundry index is populated** (run `scripts/index_foundry_docs.py`) — or record against local live mode — so grounding shows real green badges, not all-unverified.
- Use a **generic** business prompt as the hero; keep the relationship example brief and respectful (it demonstrates range without dwelling on sensitive detail).
- Keep cursor movements deliberate and slow on the trace and grounding panels — those two shots carry the whole pitch.
