# Hxrizxn AI Handoff

Date: 2026-06-10

## Current State

Hxrizxn AI is implemented as a runnable local MVP with an Azure-ready production skeleton. The app currently runs in local demo/mock mode. Azure resources have not been provisioned yet, because cloud deployment requires account login, subscription/resource group choices, container registry setup, secrets, and potentially billable resources.

Local app endpoints:

- Web: `http://localhost:3000`
- API: `http://127.0.0.1:8000`
- API health: `http://127.0.0.1:8000/api/health`

Current API health response confirms:

- `ok: true`
- `service: hxrizxn-api`
- `demo_mode: true`
- `foundry_iq_configured: false`

## What Is Implemented

### Backend

- FastAPI app in `apps/api`.
- Pydantic v2 JSON contracts in `apps/api/app/schemas.py`.
- SQLAlchemy models and Alembic migration for requested entities:
  - users
  - decision_cases
  - decision_options
  - scenarios
  - scenario_impacts
  - scenario_risks
  - experiment_plans
  - agent_runs
  - documents
  - final_recommendations
- Deterministic HORIZON-X agent workflow.
- Microsoft Agent Framework dependency and runtime adapter.
- Foundry IQ-ready `KnowledgeProvider` abstraction with local mock fallback.
- Azure/OpenAI-ready `ModelProvider` abstraction with local mock fallback.
- Local object storage abstraction with an Azure Blob replacement seam.
- Upload validation, sensitive text redaction, prompt-injection sanitization, secure headers, and rate-limit middleware.
- Persisted agent traces and report generation.

### Current Agent Workflow

The current orchestrator includes these visible workflow steps:

1. Decision Framing Agent
2. Evidence Grounding Agent
3. Assumption Miner Agent
4. Scenario Lattice Agent
5. Ripple Effects Agent
6. Regret and Reversibility Agent
7. Black Swan Agent
8. Future Self Agent
9. Experiment Design Agent
10. Safety and Boundary Agent
11. Recommendation Composer Agent

Note: this is slightly expanded from the original nine-agent request because grounding, assumption mining, and future-self postcard generation were split into explicit nodes for clearer traceability.

### Frontend

- Next.js 16 App Router app in `apps/web`.
- TypeScript, Tailwind CSS v4, Zustand, Framer Motion.
- React Flow visualizations:
  - scenario lattice graph
  - agent workflow trace graph
- ECharts visualizations:
  - radar chart
  - risk heatmap
  - stacked impact chart
  - optionality vs reversibility quadrant
- Screens implemented:
  - landing page
  - decision intake
  - animated analysis loading screen
  - scenario comparison
  - ripple/risk analysis
  - experiment plan
  - decision memo and report export
- Local demo fallback if the API/cloud path is unavailable.
- shadcn-compatible local Button primitive in `apps/web/components/ui/button.tsx`.

### Data, Docs, and Ops

- Synthetic demo data in `demo-data`.
- Golden eval cases in `evals/golden_cases.json`.
- Latest eval output in `evals/latest-results.json`.
- JSON schema export script and generated schemas in `packages/types/schemas`.
- Versioned prompt library in `packages/agent-prompts`.
- Azure Bicep scaffold in `infra/bicep/main.bicep`.
- GitHub Actions workflows:
  - CI
  - Docker build
  - Azure deploy
- Dockerfiles for API and web.
- `docker-compose.yml` for local API/web/Postgres stack.
- Documentation:
  - `README.md`
  - `docs/architecture.md`
  - `docs/agents.md`
  - `docs/api.md`
  - `docs/deployment.md`
  - `docs/demo.md`
  - `docs/safety.md`
  - `docs/evals.md`
  - `docs/prompt-library.md`
  - `docs/file-by-file.md`

## Verification Results

These were run against the current worktree.

```text
pytest apps/api/tests
Result: 7 passed
```

```text
npm --workspace apps/web run test
Result: 1 passed
```

```text
npm --workspace apps/web run build
Result: passed
```

```text
npm --workspace apps/web run test:e2e
Result: 2 passed, desktop and mobile
```

```text
python scripts/run_evals.py
Result: 5 cases, average score 9.6
Output: evals/latest-results.json
```

Known test warnings:

- FastAPI `on_event` deprecation warning. The app works; future cleanup should migrate startup logic to lifespan handlers.
- Microsoft Agent Framework experimental warnings from installed framework internals.

## Local Runtime Artifacts

These local files are generated and should not be committed:

- `node_modules/`
- `.next/`
- `hxrizxn.db`
- `api-server.log`
- `web-server.log`
- `output/playwright/`

Screenshots were captured locally under `output/playwright/`, but `output/` is now ignored by git.

## Current Worktree Summary

Tracked files currently modified include:

- `README.md`
- `.gitignore`
- `apps/api/app/agents/regret.py`
- `apps/api/app/api/routes.py`
- `apps/api/app/services/orchestrator.py`
- `apps/api/pyproject.toml`
- `apps/api/tests/conftest.py`
- `apps/web/README.md`
- `docs/architecture.md`
- `package.json`

Major new/untracked project areas include:

- `.github/workflows`
- `apps/api/app/agents/assumption.py`
- `apps/api/app/agents/future_self.py`
- `apps/api/app/agents/grounding.py`
- `apps/api/app/providers/storage.py`
- `apps/web`
- `demo-data`
- `docs`
- `evals/latest-results.json`
- `infra`
- `package-lock.json`
- `packages`

## Known Caveats

- Azure has not been deployed yet.
- Foundry IQ is not configured locally, so the app uses `MockKnowledgeProvider`.
- Azure OpenAI/Foundry model calls are scaffolded but local analysis is deterministic mock logic for demo reliability.
- `npm audit --omit=dev` reports 2 moderate advisories in Next's transitive `postcss`; npm suggests a breaking `--force` remediation, so no forced downgrade was applied.
- The API currently uses `Base.metadata.create_all()` on startup for local convenience. Alembic migration exists and should be used in production deployment.
- Auth is demo/stub mode only. Microsoft Entra/OAuth is architected as future work.

## What Is Remaining

### 1. Azure Deployment

This is the biggest remaining area. The repo is Azure-ready, but no Azure resources have been provisioned yet.

| Azure item | Status | Remaining work |
| --- | --- | --- |
| Azure resources provisioned | Not done | Need Azure login, subscription, and resource group |
| Azure Container Registry | Not done | Need ACR creation or selection |
| API image pushed to ACR | Not done | Need Docker build, tag, login, and push |
| Bicep deployment executed | Not done | Need `az deployment group create` |
| Backend deployed to Azure Container Apps | Not done | Needs deployment |
| Frontend deployed to Azure Static Web Apps | Not done | Needs deployment |
| Azure PostgreSQL live database | Not done | Needs provision and config |
| Azure Blob Storage live storage | Ready, not deployed | Bicep resource and app provider wiring exist; needs Azure deployment |
| Azure Key Vault secrets | Scaffolded only | Key Vault resource exists, secrets not configured |
| Azure Monitor/App Insights | Scaffolded only | Bicep resources exist, deployment not executed and app telemetry not fully wired |

Honest claim: "Azure-ready skeleton exists."

Do not claim yet: "Hxrizxn AI is deployed on Azure."

### 2. Foundry IQ

| Item | Status |
| --- | --- |
| Foundry IQ abstraction | Completed |
| MockKnowledgeProvider fallback | Completed |
| Real Foundry IQ credentials | Not done |
| Real Foundry IQ retrieval | Not confirmed live |
| Foundry IQ knowledge base/index | Not done |
| Citation-backed grounding from Foundry IQ | Not confirmed |

Honest claim: "Foundry IQ-ready provider abstraction is implemented."

Do not claim yet: "Hxrizxn AI uses Foundry IQ in production."

### 3. Azure OpenAI / Live LLM Calls

| Item | Status |
| --- | --- |
| ModelProvider abstraction | Completed |
| Local mock fallback | Completed |
| Azure/OpenAI-ready config seam | Completed |
| Real Azure OpenAI endpoint configured | Not done |
| Real Azure OpenAI API key configured | Not done |
| Real Azure OpenAI deployment selected | Not done |
| Live LLM-powered analysis | Not active locally |

Honest claim: "The MVP currently runs in deterministic demo mode with Azure OpenAI-ready provider seams."

Do not claim yet: "Every agent is powered by Azure OpenAI."

### 4. Microsoft Agent Framework

| Item | Status |
| --- | --- |
| Dependency installed | Completed |
| Runtime adapter | Completed |
| Experimental warnings | Known |
| Deep/native Agent Framework orchestration | Partial/scaffolded |

Honest claim: "Includes Microsoft Agent Framework adapter support and an Azure-ready agent orchestration layer."

Do not claim yet: "Built entirely on Microsoft Agent Framework."

### 5. Authentication

| Item | Status |
| --- | --- |
| Demo/stub auth | Acceptable for local demo |
| Real user auth | Not done |
| Microsoft Entra/OAuth | Not done |
| Role-based access control | Not done |

### 6. Production Database Setup

| Item | Status |
| --- | --- |
| SQLAlchemy models | Completed |
| Alembic migration | Completed |
| Local `create_all` startup | Completed for convenience |
| Production migration workflow | Remaining |
| Deployed DB migration | Not done |

Required deployed command after Azure database configuration:

```powershell
alembic upgrade head
```

### 7. Security Hardening

| Security item | Status |
| --- | --- |
| Upload validation | Completed |
| Redaction | Completed |
| Prompt-injection sanitization | Completed |
| Secure headers | Completed |
| Rate limiting | Completed |
| Secrets in Key Vault | Not done |
| Secret rotation | Remaining before public push/deploy |
| Real auth | Not done |
| Production CORS hardening | Not confirmed |
| Content Safety integration | Not implemented |
| Crisis/self-harm handling | Basic flagging exists; user-facing crisis flow needs hardening |

### 8. Observability

| Item | Status |
| --- | --- |
| Local logs | Completed |
| Persisted agent traces | Completed |
| Agent trace graph in UI | Completed |
| Azure Monitor/App Insights resources | Scaffolded in Bicep only |
| Application telemetry wiring | Remaining |
| Token usage tracking | Schema field exists; real provider tracking not active |
| Latency dashboard | Not done |
| Per-agent telemetry dashboard | Not done |

For the hackathon MVP, persisted traces plus the UI workflow graph are usable. A stronger Microsoft-style deployment should add App Insights or Foundry tracing.

### 9. Dependency / Warning Cleanup

| Item | Status |
| --- | --- |
| FastAPI runtime | Working |
| FastAPI `on_event` warning | Remaining cleanup |
| Microsoft Agent Framework warning | Known/acceptable |
| npm audit moderate advisories | Remaining/unresolved |
| Forced breaking remediation | Not applied |

## Azure Deployment Next Steps

1. Confirm Azure subscription ID.
2. Run the recommended no-local-Docker deployment script:

```powershell
az login
.\scripts\deploy_azure_recommended.ps1 `
  -SubscriptionId "<subscription-id>" `
  -Location "eastus" `
  -ResourceGroup "rg-hxrizxn-demo"
```

The script creates or reuses ACR, builds both images in ACR, deploys Bicep, wires Blob Storage into the API, and prints the live API/web URLs.

3. If using real Foundry IQ or Azure OpenAI, rerun or update Container Apps with:

```powershell
.\scripts\deploy_azure_recommended.ps1 `
  -SubscriptionId "<subscription-id>" `
  -FoundryIqEndpoint "<endpoint>" `
  -FoundryIqApiKey "<key>" `
  -AzureOpenAiEndpoint "<endpoint>" `
  -AzureOpenAiApiKey "<key>" `
  -AzureOpenAiDeployment "<deployment-name>" `
  -DemoMode $false
```

4. Configure or rotate secrets as needed:

- `AZURE_FOUNDRY_PROJECT_ENDPOINT`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_DEPLOYMENT`
- `FOUNDRY_IQ_ENDPOINT`
- `FOUNDRY_IQ_API_KEY`
- `FOUNDRY_IQ_INDEX_NAME`

5. Run database migrations in the deployed environment if you disable local `create_all` startup:

```powershell
alembic upgrade head
```

6. Verify:

```powershell
Invoke-RestMethod "<api-url>/api/health"
Start-Process "<web-url>"
```

## Recommended Immediate Review Checklist

- Confirm whether the expanded 11-step trace should remain or be renamed back to the original nine requested agents.
- Decide whether to commit local verification screenshots or rely only on SVG mockups in `apps/web/public/mockups`.
- Replace mock Foundry IQ retrieval with real Foundry IQ calls after credentials are available.
- Decide the Azure resource naming convention and region before deployment.
- Rotate any temporary secrets before pushing a public repo.
