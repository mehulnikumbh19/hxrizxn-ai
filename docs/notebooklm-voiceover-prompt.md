# NotebookLM Voiceover Prompt — Hxrizxn AI Demo

## How to use this
1. Open NotebookLM → create a new notebook.
2. Add sources: paste this whole file as a source. (Optionally also add `README.md`, `SUBMISSION.md`, and `docs/demo-video-script-3min.md` as extra sources for richer detail.)
3. Use the **instruction prompt** at the bottom to generate the voiceover (via Audio Overview "customize", or by asking it to produce a narrated script you then read / TTS).
4. Target length: a ~3-minute spoken narration (≈430–470 words). Keep it under 5 minutes.

---

## PROJECT BRIEF — everything NotebookLM needs to know

### What Hxrizxn AI is
Hxrizxn AI is a **multi-agent reasoning system for high-stakes decisions**, built for the Microsoft Agents League **Reasoning Agents** track. It takes one hard, real-world decision and reasons through it with **eleven specialized AI agents**, producing not a single confident answer but a full, evidence-grounded analysis across multiple possible futures. The name is "HORIZON" with the certainties crossed out — every "o" (a closed, known thing) replaced with an "x" (an open question).

### The core idea
Most AI tools answer instantly and confidently, even when guessing. For decisions you can't undo, that false confidence is dangerous. Hxrizxn is the opposite: it reasons in explicit, inspectable steps, **grounds every claim in evidence and cites the source — or honestly marks it "unverified" and abstains** rather than asserting something it can't support.

### Built with (technology)
- **Microsoft Foundry** — Azure OpenAI (model `gpt-4.1-mini`) powers the reasoning agents.
- **Foundry IQ** (Azure AI Search) — the grounded knowledge layer; agents retrieve from an indexed knowledge base and cite sources.
- **Microsoft Agent Framework** — orchestration integration point.
- **Azure Container Apps** — the app is deployed live (API + web), with Bicep infrastructure-as-code and GitHub Actions deployment.
- Frontend: Next.js. Backend: FastAPI with typed Pydantic contracts. All knowledge documents are **synthetic** (no real or personal data).

### The eleven agents (the HORIZON-X pipeline, in order)
1. **Decision Framing** — turns a messy story into a structured problem: goals, fears, constraints, options.
2. **Evidence Grounding** — retrieves cited evidence from Foundry IQ; tags every downstream claim as grounded or unverified.
3. **Assumption Miner** — surfaces the hidden assumptions the decision secretly depends on.
4. **Scenario Lattice** — branches into three futures: optimistic, base, and stress, each with a scorecard.
5. **Ripple Effects** — maps second- and third-order consequences across six life/business domains.
6. **Regret & Reversibility** — measures how permanent each path is and what undoing it costs.
7. **Black Swan** — hunts low-probability, high-impact risks and plants early-warning tripwires.
8. **Future Self** — checks the decision against who you'll be years later.
9. **Experiment Design** — designs the cheapest reversible test to reduce the biggest unknown.
10. **Safety & Boundary** — pure rule checks for high-stakes domains; can abort the run. (Deliberately has no fallback — it fails loudly.)
11. **Recommendation Composer** — writes the final memo: recommendation, uncertainty bands, citations, disclaimers.

### The pages / user workflow (narrate in this order)
1. **Landing page** — the entry point; introduces the "solve for x" concept and the live app.
2. **Intake page** — the user types the decision in plain language plus goals, fears, constraints, money limit, and time horizon, then clicks Analyze.
3. **Loading page ("Behind the scenes" trace)** — shows the eleven agents running live, each with its real status and latency. This proves it's genuine multi-step reasoning, not a single call.
4. **Scenarios page** — the three computed futures (optimistic / base / stress) with scorecards and visualizations (radar chart, optionality quadrant).
5. **Ripple page** — a risk heatmap and impact cascade across domains, plus the **Evidence & Honesty panel**: each assumption and risk shown with a green "Grounded" badge (and its cited Foundry IQ source) or an amber "Unverified" badge where the agent abstains. The black-swan risk stays unverified on purpose.
6. **Experiment page** — a cheap, reversible 30-day test with a pre-committed kill metric, instead of an irreversible choice.
7. **Memo page** — the final recommendation with probability bands (not point estimates), citations, and clear disclaimers that it is decision *support*, not a licensed advisor.

### The decision domain (range)
Hxrizxn targets high-stakes **enterprise decisions** first — build-vs-buy, vendor selection and lock-in, hiring and headcount, market entry, strategic bets and capital allocation. The **same engine** also reasons through personal and even emotional decisions, which proves the reasoning generalizes rather than being hard-coded to one scenario.

### What makes it stand out (emphasize these)
- **Cite-or-abstain grounding** — trustworthy, anti-hallucination reasoning. The headline feature.
- **Eleven inspectable agents with a live trace** — real multi-step reasoning you can watch.
- **Grounded in Foundry IQ with citations.**
- **Range** — one engine, enterprise and personal decisions.
- **Live on Azure**, production-deployed, safety gate built in.

---

## INSTRUCTION PROMPT (paste this to NotebookLM to generate the voiceover)

> Using the project brief in the sources, write a **single-narrator voiceover script for a 3-minute product demo video** of Hxrizxn AI. Target **440–470 words** so it reads in about three minutes at a natural pace.
>
> Requirements:
> - Write it as **continuous spoken narration** (first-person product voice, confident but warm), NOT bullet points — it will be read aloud or fed to text-to-speech.
> - Follow the demo page order exactly: **Landing → Intake → Loading/Behind-the-scenes trace → Scenarios → Ripple (Evidence & Honesty) → Experiment → Memo → close.** Write one short narration beat per page so it syncs to on-screen footage.
> - **Open with a hook** about the danger of confident AI answers for decisions you can't undo.
> - **Spend the most time on two things:** (1) the eleven-agent live reasoning trace, and (2) the cite-or-abstain Evidence & Honesty panel (grounded vs unverified, with the black-swan deliberately unverified). These are the differentiators.
> - Use a concrete example throughout: a company weighing a **$900,000 enterprise contract** that delays the roadmap and risks engineering burnout.
> - Mention it's built on **Microsoft Foundry and Foundry IQ** and **live on Azure**.
> - End with the tagline: **"Hxrizxn — solve for x, before life solves it for you."**
> - Keep sentences short and clear for spoken delivery. No jargon dumps. No reading out URLs.
>
> Output only the finished narration script, with light `[Landing]`, `[Intake]`, `[Trace]`, etc. scene tags at the start of each beat so I can sync it to footage.

---

## Tip for generating the audio
- In NotebookLM, the **Audio Overview** feature makes a two-host conversational podcast by default. For a clean single-narrator voiceover, instead ask it (with the instruction prompt above) to **produce the written script**, then run that script through a text-to-speech tool, or read it yourself over the screen recording. If you do use Audio Overview, customize it and tell it to act as a single narrator delivering the script above.
