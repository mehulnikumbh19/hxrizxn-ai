# File-by-File Implementation

## Root

- `README.md`: executive summary, setup, architecture, workflow, Gantt, risks, commands.
- `.env.example`: local, Azure, Foundry IQ, and frontend configuration.
- `docker-compose.yml`: local Postgres with pgvector, API, and web containers.
- `.github/workflows/*.yml`: CI, Docker build, and Azure deploy workflow.

## Backend

- `apps/api/app/main.py`: FastAPI app, CORS, secure headers, rate limiting, router registration.
- `apps/api/app/api/routes.py`: required API routes, demo endpoint, uploads, reports.
- `apps/api/app/schemas.py`: Pydantic v2 JSON contracts for all requested schemas.
- `apps/api/app/db/models.py`: SQLAlchemy models for all requested entities.
- `apps/api/alembic/versions/0001_initial_hxrizxn_schema.py`: initial migration.
- `apps/api/app/agents/*.py`: deterministic HORIZON-X agent implementations.
- `apps/api/app/providers/knowledge.py`: Foundry IQ and mock retrieval providers.
- `apps/api/app/providers/model.py`: Azure Foundry/OpenAI/mock model provider abstraction.
- `apps/api/app/providers/storage.py`: local object storage provider with Azure Blob seam.
- `apps/api/app/services/orchestrator.py`: multi-agent workflow, persisted traces, persistence.
- `apps/api/app/services/security.py`: safety helpers, upload validation, prompt-injection resistance.
- `apps/api/tests/*.py`: API, schema, safety, retrieval, and report tests.

## Frontend

- `apps/web/app/page.tsx`: app entry.
- `apps/web/components/HxrizxnApp.tsx`: full product flow.
- `apps/web/components/ScenarioLattice.tsx`: React Flow scenario lattice.
- `apps/web/components/AgentTraceGraph.tsx`: React Flow agent trace graph.
- `apps/web/components/DecisionCharts.tsx`: ECharts radar, heatmap, impact stack, quadrant.
- `apps/web/lib/api.ts`: API client with demo fallback.
- `apps/web/lib/useDecisionStore.ts`: Zustand screen/package state.
- `apps/web/components/ui/button.tsx`: shadcn-compatible local Button component.
- `apps/web/public/mockups/*.svg`: required wireframe mock screens.
- `apps/web/__tests__/api.test.ts`: Vitest smoke test.
- `apps/web/e2e/app.spec.ts`: Playwright demo flow test.

## Infra and Ops

- `infra/bicep/main.bicep`: Azure Container Apps, Postgres, Storage, Key Vault, Monitor, Static Web App.
- `scripts/seed_demo_data.py`: seeds five demo cases.
- `scripts/export_schemas.py`: exports JSON schemas.
- `scripts/run_evals.py`: deterministic eval harness.
- `scripts/deploy_azure_recommended.ps1`: no-local-Docker Azure deployment script using ACR cloud builds and Container Apps.
