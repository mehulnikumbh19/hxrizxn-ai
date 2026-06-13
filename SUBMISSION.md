# Hxrizxn AI — Agents League Submission

**Track:** 🧠 Reasoning Agents
**Built with:** Microsoft Foundry (Azure OpenAI for reasoning, Foundry IQ / Azure AI Search for grounding), deployed on Azure Container Apps.

---

## One-liner

**Most agents answer. Hxrizxn reasons through your decision across futures — then cites its evidence or admits what it can't know.**

Hxrizxn AI is a multi-agent decision simulator for high-stakes, one-way-door decisions. Eleven specialized reasoning agents take a single real-world dilemma and work through it the way a careful advisor would: framing the choice, gathering evidence, surfacing hidden assumptions, branching into optimistic / base / stress futures, mapping second-order ripple effects, weighing regret and reversibility, hunting black-swan risks, and composing a grounded recommendation — with every claim tagged **grounded** (cited to a source) or **unverified** (honestly abstained).

## The problem

Organizations — and people — make irreversible decisions with confident-sounding tools that hallucinate. A single LLM call will happily assert "build it in-house, it'll be cheaper" or "this market will pay off this year" with no evidence and no humility. For decisions that can't be undone, that confidence is the danger.

**Decision domain.** Hxrizxn targets high-stakes **enterprise decisions** first — build-vs-buy, vendor selection and lock-in, hiring and headcount, market entry, strategic bets and capital allocation — each grounded in Foundry IQ or honestly flagged as unverified. The same engine generalizes to personal and even emotional decisions, which proves the reasoning isn't hard-coded to a single scenario.

## Track fit (Reasoning Agents + Microsoft Foundry)

This submission implements the track's core pattern — multi-agent orchestration, **Foundry IQ** grounded-and-cited retrieval (the required Microsoft IQ layer), and production deployment on Azure Container Apps — applied to enterprise and personal **decision intelligence**. The starter scenarios (Enterprise Learning, Role-Play Game) are illustrations of the *kind* of system to build; Hxrizxn brings the same multi-agent + Foundry IQ + deployment pattern to a different, defensible decision-support domain.

## What makes it a *reasoning* agent (not a wrapper around one call)

**1. Eleven explicit, inspectable reasoning stages.** The HORIZON-X pipeline runs eleven named agents, each producing structured, auditable output:

> Decision Framing → Evidence Grounding → Assumption Miner → Scenario Lattice → Ripple Effects → Regret & Reversibility → Black Swan → Future Self → Experiment Design → Safety & Boundary → Recommendation Composer

A live "Behind the scenes" trace shows each agent's status and real latency — you can watch the reasoning happen, not just read a final answer.

**2. Cite-or-abstain grounding (the headline feature).** Every assumption and risk is checked against the Foundry IQ knowledge base. If a claim is supported, the agent shows the **Grounded** badge and the source it cites. If nothing supports it, the agent marks it **Unverified** and abstains from asserting it as fact. A black-swan risk — speculative by nature — is always left unverified, on purpose. This is what separates trustworthy reasoning from confident guessing.

**3. It reasons about decisions that actually matter — including emotional ones.** The same engine that evaluates a $900k enterprise contract (revenue timing, engineering capacity, customer-concentration risk) also reasons through a genuinely hard personal dilemma — "should I be honest with my partner?" — surfacing emotional backlash, hidden resentment, isolation risk, and the value of taking responsibility, each grounded in relationship decision-science or honestly flagged as uncertain. The reasoning generalizes across business *and* human decisions, and a dedicated Safety & Boundary agent watches for high-stakes emotional or wellbeing situations.

## Built on Microsoft Foundry

- **Azure OpenAI** (deployment `gpt-4.1-mini`) powers every reasoning agent.
- **Foundry IQ / Azure AI Search** is the grounding backend. A re-indexing pipeline (`scripts/index_foundry_docs.py`) loads decision-science knowledge into the index; agents retrieve from it and cite it by source.
- **Azure Container Apps** hosts the API and web app; secrets live in Container App secrets, never in code.

## Why it stands out in the Reasoning Agents field

The category is crowded with certification and career coaches. Hxrizxn occupies a near-empty lane — multi-future decision simulation — and matches the trustworthiness bar set by the strongest entries by doing what they do: **grounding its claims and abstaining when it can't.** The grounded-vs-unverified contrast is visible, the multi-agent structure earns its keep, and the emotional use case makes the reasoning relatable, not abstract.

## Honesty, safety, and responsible AI

- **Cite-or-abstain** is a built-in anti-hallucination mechanism: the agent would rather say "unverified" than assert a falsehood.
- A **Safety & Boundary agent** flags high-stakes emotional, financial, and wellbeing situations.
- **No personal data is stored in the repository.** Demo knowledge is generic; the runtime database is git-ignored; secrets are never committed (see `SECURITY.md`).
- Outputs are framed as **plausible simulations, not predictions** — surfaced explicitly as an assumption.

## Demo flow (2–3 minutes)

1. Open the live app, enter a real decision (try the enterprise-contract prompt, then the relationship prompt to show range).
2. Watch the **Behind the scenes** trace — eleven agents reasoning live with real timings.
3. Open **Ripple Effects** → the **Evidence & Honesty** panel: point to a green **Grounded** claim citing a Foundry IQ source, and an amber **Unverified** claim where the agent abstains.
4. Land on the recommendation memo — grounded, hedged, honest about what it doesn't know.

## Try it

- Local: `npm run dev` → http://localhost:3000 (set up `.env` from `.env.example`).
- Reproduce the agent trace + grounding: run a decision, open the Ripple Effects screen.

---

*Hxrizxn AI — a second opinion for the decisions you can't take back.*
