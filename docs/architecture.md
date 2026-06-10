# Hxrizxn AI — Architecture

## System overview

Hxrizxn AI follows a **magentic manager** pattern: specialized agents own one kind of thinking, hand off structured artifacts, and stream observable traces to the UI.

```mermaid
flowchart LR
    U[User in Web App] --> FE[Next.js Frontend]
    FE --> AGUI[AG-UI Streaming Layer]
    AGUI --> ORCH[Microsoft Agent Framework Orchestrator]

    ORCH --> DFA[Decision Framing Agent]
    ORCH --> EGA[Evidence Grounding Agent]
    ORCH --> AMA[Assumption Miner Agent]
    ORCH --> SCA[Scenario Architect Agent]
    ORCH --> SOA[Second-Order Effects Agent]
    ORCH --> RRA[Regret and Reversibility Agent]
    ORCH --> BSA[Black Swan Agent]
    ORCH --> FSA[Future Self Agent]
    ORCH --> EDA[Experiment Design Agent]
    ORCH --> RSA[Recommendation and Synthesis Agent]
    ORCH --> SBA[Safety and Boundary Agent]

    EGA --> IQ[Foundry IQ Knowledge Base via MCP]
    IQ --> KB[Decision Science and Domain Knowledge Sources]

    ORCH --> DB[Session and Trace Store]
    ORCH --> EVAL[Foundry Evaluations and Observability]

    FE --> VIZ[Scenario Lattice, Risk Heatmap, Timelines]
    RSA --> FE
    SBA --> FE
    EVAL --> FE
```

## Workflow phases

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Orchestrator
    participant Frame as Framing Agent
    participant IQ as Foundry IQ
    participant Scenarios as Scenario Lattice
    participant Ripple as Ripple / Risk / Regret
    participant Exp as Experiment Design
    participant Composer as Recommendation Composer

    User->>API: POST /cases (intake)
    User->>API: POST /cases/{id}/analyze
    API->>Frame: Frame decision + safety scan
    Frame->>IQ: Retrieve evidence
    IQ-->>Frame: Citations bundle
    API->>Scenarios: Build optimistic / base / stress branches
    par Concurrent analysis
        API->>Ripple: Map second-order effects
        API->>Ripple: Identify risks + black swans
        API->>Ripple: Score regret + optionality
    end
    API->>Exp: Design 7/30/90-day experiments
    API->>Composer: Synthesize decision memo
    API-->>User: Analysis package + agent traces
```

### Phase 1 — Sequential framing

1. **Decision Framing** — Parse raw dilemma into goals, fears, constraints, candidate options.
2. **Evidence Grounding** — Query Foundry IQ (or demo KB) for decision-science frameworks and domain facts.
3. **Assumption Mining** — Surface hidden premises and confidence gaps.

### Phase 2 — Concurrent scenario analysis

4. **Scenario Architect** — Generate optimistic, base, and stress futures per option.
5. **Second-Order Effects** — Ripple map across finances, career, relationships, mobility, identity.
6. **Risk + Black Swan** — Common, hidden, and tail-risk identification.
7. **Regret + Reversibility** — One-way vs two-way door scoring, optionality index.

### Phase 3 — Synthesis

8. **Future Self** — Narrative cards grounded in scenario facts.
9. **Experiment Design** — Lowest-cost reversible tests before commitment.
10. **Recommendation Composer** — Proceed / experiment / delay / do-not-proceed verdict.
11. **Safety & Boundary** — Policy enforcement on every stage.

## Memory layers

| Layer | Scope | Contents |
|---|---|---|
| Session memory | Active thread | Raw intake, UI state |
| Case memory | Per decision | Brief, assumptions, evidence, scenarios |
| Narrative memory | UX continuity | Future-self cards, explanations |
| Audit memory | Observability | Agent traces, scores, eval metadata |

## Data model (MVP)

Core entities persisted in SQLite (local) or Postgres (Docker):

- `DecisionCase` — intake and structured context
- `DecisionOptionDB` — candidate paths
- `ScenarioDB` + `ScenarioImpactDB` + `ScenarioRiskDB` — lattice nodes
- `ExperimentPlanDB` — ranked de-risking actions
- `FinalRecommendationDB` — verdict and rationale
- `AgentRunDB` — per-agent input/output traces
- `DocumentDB` — optional uploaded context (sanitized)

## X-TRACE scoring dimensions

Final decision packets expose six signature scores:

| Score | Meaning |
|---|---|
| Alignment | Fit with stated values and goals |
| Evidence confidence | Grounding strength from IQ retrieval |
| Tail-risk resilience | Robustness under black-swan stress |
| Reversibility | How easily the decision can be undone |
| Regret exposure | Anticipated future-self difficulty |
| Experimentability | How much uncertainty a cheap test can collapse |

## Deployment topology

| Environment | Database | Model | IQ |
|---|---|---|---|
| Local dev | SQLite | OpenAI / Azure OpenAI fallback | Demo KB |
| Docker Compose | Postgres + pgvector | Azure OpenAI | Foundry IQ (when configured) |
| Foundry Agent Service | Managed Postgres | Azure deployment | Foundry IQ MCP |

## Frontend screens (planned)

1. **Decision Intake** — dilemma, options, values, irreversibility slider
2. **Decision Brief** — structured summary + human-in-the-loop confirm
3. **Scenario Lattice** — React Flow graph (center canvas)
4. **Risk & Ripple Console** — heatmap + causal chain
5. **Future Self & Experiment Plan** — narratives + ranked next steps
6. **Agent Trace Drawer** — live reasoning log for demo mode

## Reliability patterns

- **Deterministic demo mode** — seeded knowledge and template fallbacks when credentials are absent
- **Agent run persistence** — every stage logged to `AgentRunDB` for replay
- **Verifier agent** — output sanity checks before final synthesis
- **Golden eval cases** — `evals/golden_cases.json` regression harness via `scripts/run_evals.py`
- **Safety gates** — domain boundary detection in framing and final composition
