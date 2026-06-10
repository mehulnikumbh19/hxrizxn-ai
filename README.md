# Hxrizxn AI

**Before you step through a one-way door, Hxrizxn AI lets you test the futures on the other side.**

Hxrizxn AI is a transparent decision-simulation system for high-stakes, low-frequency, partially irreversible life choices. Instead of giving advice, it runs a multi-agent reasoning workflow that frames your dilemma, grounds claims in evidence, generates a scenario lattice, maps second-order consequences, scores regret and reversibility, and ends with a concrete low-risk experiment plan.

Built for the [Microsoft Agents League — Reasoning Agents](https://github.com/microsoft/agents-league) track, with **Microsoft Agent Framework**, **Foundry IQ**, and **AG-UI** integration.

## What it does

| Stage | Agent / module | Output |
|---|---|---|
| Intake | Decision Framing | Structured decision brief, options, missing info |
| Grounding | Evidence + Foundry IQ | Citations, frameworks, domain facts |
| Analysis | Assumption Miner, Scenario Architect | Best / base / worst / tail scenarios |
| Depth | Ripple, Risk, Regret, Optionality | Second-order map, black-swan stress, reversibility |
| Action | Experiment Design, Composer | 7/30/90-day experiments, final recommendation |
| Safety | Safety & Boundary | Escalations, abstentions, policy checks |

The proprietary methodology is **X-TRACE**: **e**Xtract → **T**est → **R**ender → **A**nalyze → **C**ompare → **E**xperiment.

## Architecture

```
User → Next.js Frontend → AG-UI Streaming → Agent Framework Orchestrator
                                              ├── Framing / Grounding / Scenarios
                                              ├── Ripple / Risk / Regret / Experiments
                                              ├── Foundry IQ (MCP knowledge layer)
                                              └── SQLite or Postgres + trace store
```

See [docs/architecture.md](docs/architecture.md) for the full diagram and agent contracts.

## Repository layout

```
hxrizxn-ai/
├── apps/
│   ├── api/          # FastAPI backend + multi-agent orchestrator
│   └── web/          # Next.js decision cockpit (in progress)
├── docs/
│   ├── architecture.md
│   └── research-report.md
├── evals/            # Golden demo cases for regression
├── scripts/          # Seed data, eval runner, schema export
├── docker-compose.yml
└── hxrizxn.md        # Original strategy & research brief
```

## Quick start

### Prerequisites

- Python 3.12+
- Node.js 20+ (for frontend workspace)
- Docker (optional, for Postgres + full stack)

### 1. Clone and configure

```bash
git clone https://github.com/mehulnikumbh19/hxrizxn-ai.git
cd hxrizxn-ai
cp .env.example .env
```

`DEMO_MODE=true` runs without Azure credentials using seeded knowledge and deterministic fallbacks.

### 2. Backend (API)

```bash
cd apps/api
python -m pip install -e ".[dev]"
cd ../..
python scripts/seed_demo_data.py
python -m uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

API docs: http://localhost:8000/docs

### 3. Full stack with Docker

```bash
docker compose up --build
```

- API: http://localhost:8000
- Web: http://localhost:3000 (when `apps/web` is present)

### 4. Run tests and evals

```bash
pytest apps/api/tests
python scripts/run_evals.py
```

## API overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service status, demo mode, IQ config |
| `POST` | `/api/cases` | Create a decision case |
| `POST` | `/api/cases/{id}/analyze` | Run the full HORIZON-X workflow |
| `GET` | `/api/cases/{id}/report` | Markdown decision packet |
| `GET` | `/api/sample-prompt` | Seeded demo dilemma |

## Microsoft stack integration

| Layer | Technology | Role |
|---|---|---|
| Orchestration | Microsoft Agent Framework | Sequential + concurrent agent workflow |
| Knowledge | Foundry IQ via MCP | Permission-aware retrieval with citations |
| Runtime | Foundry Agent Service | Managed deployment target |
| UI streaming | AG-UI | Live agent traces, approvals, state sync |
| Evaluation | Foundry evaluators | Quality, safety, and agent-behavior checks |

Configure Azure credentials in `.env` when moving off demo mode. See `.env.example` for all variables.

## Demo storyline

Recommended five-minute demo decision:

> *Should I quit my software job, move to another country for graduate school, and delay launching my startup — or stay employed and test the startup on the side first?*

Flow: intake → decision brief → agent trace fan-out → scenario lattice → ripple chain → reversibility/regret scores → future-self cards → experiment plan.

## Safety boundaries

Hxrizxn AI is **not** therapy, legal advice, or licensed financial advice. It labels outputs as **simulations**, not predictions; refuses crisis-adjacent content; and stores minimal session data. Use synthetic personas for public demos.

## Research & strategy

The full competitive landscape, product strategy, agent specs, and contest positioning live in [docs/research-report.md](docs/research-report.md) (sourced from the original deep-research brief).

## License

MIT — see [LICENSE](LICENSE).

## Author

Mehul Nikumbh — Microsoft Agents League submission.
