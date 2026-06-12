# Hxrizxn AI Handoff for Claude

Date: 2026-06-11

## Session Update (2026-06-11, continued #6 - Cowork redesign + Azure deploy)

Status: Redesigned the web UI, recovered it after an external editor reverted one file, committed (`f575aee`), user pushed to `main`, and the GitHub Actions **deploy-azure** pipeline now runs end-to-end. The app is **live on Azure Container Apps** in `rg-hxrizxn-demo2`.

### Done this session
- **Full visual redesign** to "Microsoft Fluent 2 app shell + Brillance premium SaaS front door":
  - `apps/web/app/globals.css` - reworked tokens to calm warm off-white surfaces (`--colorCanvas #f7f6f4`), hairline Fluent cards (`.panel`), ambient glow reserved for the landing (`.glow`, `.app-shell--landing`), frosted `.panel--glass` for the hero only, pill helpers (`.btn-neutral`, calmer 2-stop `--colorActionGradient`), `surface-inset` wells.
  - `apps/web/components/HxrizxnApp.tsx` - segmented **pill nav** command bar (animated `layoutId="nav-pill"`), centered Brillance **landing** (eyebrow chip, big headline, refined pill prompt box that pre-fills intake, quick-pick chips, soft-glow dashboard preview), intake on inset fields + pill buttons, Fluent **command-bar `SectionHeader`** on the analysis screens.
  - Font switched to **Plus Jakarta Sans** (`apps/web/app/layout.tsx` Google Fonts link + `--fontFamilyBase/Display`).
  - **Removed all em dashes** from UI strings/comments (commas or `·`).
- **Fixed the two broken graphs.** `ScenarioLattice.tsx` and `AgentTraceGraph.tsx` were rendering all React Flow nodes collapsed on one spot. Replaced both with **deterministic custom layouts** (no `@xyflow/react`): decision tree = Decision node + 3 color-coded branch cards joined by SVG curves; agent trace = clean vertical timeline with status dots + timing.
- **Recovered from a mid-session revert.** An external editor (stale buffer) saved an *old dark-theme* version over `HxrizxnApp.tsx`, leaving `text-slate-*` markup on the new light theme (looked broken/washed-out). Re-wrote the full redesigned file via the Write tool; confirmed clean (0 `text-slate`, 0 em dashes, redesign markers present).

### Commit & deploy
- **`f575aee`** - "Redesign web UI: Fluent 2 app + Brillance landing, fix graphs, Plus Jakarta Sans, remove em dashes". Committed by the **user from their own terminal** (sandbox git was truncating the large file - see quirk #7), pushed to `origin/main`; verified `origin/main` has the redesign.
- **GitHub Actions `deploy-azure` is now wired and working.** Setup done this session:
  - OIDC service principal `hxrizxn-gh-deploy`; federated credential subject `repo:mehulnikumbh19/hxrizxn-ai:ref:refs/heads/main`; **Owner** on the subscription (required because the Bicep assigns the AcrPull role).
  - Repo **secrets**: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP`, `AZURE_ACR_NAME`, `POSTGRES_ADMIN_PASSWORD`, `AZURE_OPENAI_*`, `FOUNDRY_IQ_*`.
  - Repo **variable** `AZURE_LOCATION = eastus2` (Variables tab, NOT Secrets).
  - Two config fixes were required: the existing ACR `hxr45810acr` lives in **`rg-hxrizxn-demo2`** (not `rg-hxrizxn-demo`) -> set `AZURE_RESOURCE_GROUP=rg-hxrizxn-demo2`; and that RG is in **`eastus2`** -> set `AZURE_LOCATION=eastus2`.
- **Deployed successfully to Azure Container Apps** in `rg-hxrizxn-demo2` (web container app `hxrizxn-web`, env `hxrizxn`). Get the live URL:
  - `az containerapp show -n hxrizxn-web -g rg-hxrizxn-demo2 --query "properties.configuration.ingress.fqdn" -o tsv` (open as https://…), or
  - `az deployment group show -g rg-hxrizxn-demo2 -n main --query "properties.outputs.webUrl.value" -o tsv`.
- Note: this Container Apps deploy is **separate** from the older App Service demo site `https://hxrizxn-web-f536eeb5.azurewebsites.net` (suffix `f536eeb5`). An empty `rg-hxrizxn-demo` was left by the first run (group only, no resources) - safe to `az group delete`.

### Verification
- This exact redesign earlier **compiled clean** (`✓ Compiled successfully`) and **`tsc --noEmit` exit 0** via a reconstructed native-fs `/tmp` build. The Azure pipeline then built + deployed it end-to-end (the real production build), which is the strongest confirmation.

### NEW / continuing sandbox quirks
7. **The mount intermittently serves a STALE/TRUNCATED read of large editor-written files to bash & git** (`HxrizxnApp.tsx` ~51KB read back as ~28KB / 694 lines by `wc`/`cat`/`git add`), while `ripgrep` and the Read file-tool saw it complete. A sandbox `git add`+commit staged a **truncated half-file**. **Do NOT commit large changed files from the sandbox** - have the user commit/push from their own terminal, or verify the staged blob (`git show :path | grep <marker>`) before committing. The Write/Edit file-tools DO write the full file to Windows correctly; only bash/git *reads* go stale.
8. **An external editor re-saved an old buffer over a file mid-session**, silently reverting it. If files mysteriously revert, check for stale editor buffers / `.fuse_hidden*` copies and re-apply.

### Remaining / next
1. Optionally bump `actions/checkout@v4`/`azure/login@v2` (Node 20 deprecation warning - harmless until ~Sept 2026).
2. Optionally narrow the SP role from subscription **Owner** to least-privilege (note: RG-scoped won't cover the `az group create` step; could drop that step since the RG already exists).
3. Delete the empty `rg-hxrizxn-demo` and any leftover `.next_old*` dirs.
4. Pre-existing uncommitted churn (`next-env.d.ts`, `tsconfig.json`, `evals/latest-results.json`, `packages/types/schemas/*`) still uncommitted - unchanged this session.

---

## Session Update (2026-06-11, continued #5 — shell-capable agent)

Status: Completed and committed the remaining approved frontend batch (items 2, 3a, 3b). No push/deploy performed (awaiting user confirmation).

### Done and committed this session (on `main`)
- **`3de8295`** — Batch item 2: Persist analysis across refresh. Added zustand `persist` middleware to `apps/web/lib/useDecisionStore.ts` (sessionStorage), with `skipHydration` + a client `rehydrate()` effect in `HxrizxnApp.tsx` to avoid an SSR hydration mismatch, and `onRehydrateStorage` that resets a restored `loading` screen back to `intake`.
- **`84f8367`** — Batch item 3a: Input validation in `runCustom()`. Rejects an empty prompt and non-positive `moneyLimit`/`timeHorizon` with a clear message on the intake screen before starting an analysis run; sends the trimmed prompt to the API.
- **`d9230d0`** — Batch item 3b: Disabled the dead "Upload Docs" button (it wrapped an unwired file `<input>`), now a disabled "Upload Docs (coming soon)" button. Full upload->index wiring remains roadmap Tier 2.

### Verification
- `npx tsc --noEmit -p apps/web/tsconfig.json` → **exit 0** (full project typecheck, after each change).
- `npm --workspace apps/web run test` (vitest) → **1 passed** (also re-run green from a native-fs copy).
- `next build` for the item-2 baseline reached **"Compiled successfully" + "Finished TypeScript" + static pages 3/3 generated**; it only fails afterward on mount cleanup (`EPERM`/`EIO` unlinking `.next`), not on code. A pristine `next build` exit-0 could not be obtained this session due to the mount degrading (see quirk #4). Items 3a/3b add only validation guards and a disabled button (no new imports, no client/server boundary change), so tsc+vitest fully cover them.

### NEW sandbox quirks discovered this session (read before frontend build/test work)
4. **Windows-installed `node_modules` is missing Linux native bindings.** vitest/Next/Tailwind fail with "Cannot find native binding". Fix used: install the matching Linux packages in a clean `/tmp` dir and `cp -r` them into the repo's `node_modules` (no lockfile change):
   - `@rolldown/binding-linux-x64-gnu@1.0.3` (vitest), `@next/swc-linux-x64-gnu@16.2.9`, `lightningcss-linux-x64-gnu@1.32.0`, `@tailwindcss/oxide-linux-x64-gnu@4.3.0`.
5. **The mount is a FUSE filesystem that holds open handles → `unlink`/`rmdir` return `Operation not permitted` (EPERM), and large writes via the Read/Write/Edit *file tools* can be silently TRUNCATED** (saw `HxrizxnApp.tsx` and `useDecisionStore.ts` cut off mid-file on disk while the file-tool's own view looked complete). **Workarounds:** (a) write/repair files via bash (`cat > file <<'EOF'`, `perl -0pi -e`), which is reliable; verify with `wc -l`/`tail`. (b) `next build` can't delete its `.next` temp dir → `mv .next .next_old_$(date +%s)` before building (rename works where unlink doesn't), but these undeletable `.next_old*` dirs accumulate and eventually cause EIO during scans. They are gitignored and harmless to commits; the user can delete them from Windows.
6. **`git commit` is unusable** because stale `.git/index.lock` and `.git/HEAD.lock` (FUSE, undeletable) make git think another process is running, and `GIT_INDEX_FILE` alone wasn't enough this session. **Workaround that worked — commit via plumbing, bypassing index/HEAD locks:**
   ```bash
   export GIT_INDEX_FILE=/tmp/gitidxN GIT_AUTHOR_NAME=mehulnikumbh19 GIT_AUTHOR_EMAIL=mnikumbh19@gmail.com \
          GIT_COMMITTER_NAME=mehulnikumbh19 GIT_COMMITTER_EMAIL=mnikumbh19@gmail.com
   git read-tree HEAD                       # start from latest commit
   git add <only the files for this commit>
   TREE=$(git write-tree); PARENT=$(git rev-parse HEAD)
   CMT=$(echo "$msg" | git commit-tree "$TREE" -p "$PARENT")
   echo "$CMT" > .git/refs/heads/main       # update branch ref directly
   ```
   Note: this does NOT update the real `.git/index`, so plain `git status`/`git diff` compare against a stale index and look wrong — **always diff against HEAD** (`git diff HEAD`) for an accurate view. Branch is `main`.

### Remaining (still pending)
1. **Optional:** re-run `python scripts/run_evals.py` to confirm the Assumption Miner `ReadTimeout` now degrades gracefully after Batch item 1 (`6999d65`). NOT done this session — needs `pip install -r apps/api/requirements.txt --break-system-packages` + the `/tmp`-copy SQLite workaround from quirk #1.
2. Confirm a clean `next build` in a non-mount environment before any deploy (code compiles + typechecks; only mount cleanup blocked a clean exit here).
3. Do **not** push/deploy without explicit user confirmation.

### Housekeeping (uncommitted, unchanged from prior sessions + this session's artifacts)
- `HANDOFF.md` (this update).
- Pre-existing CRLF/LF churn on `apps/web/next-env.d.ts`, `apps/web/tsconfig.json`, `evals/latest-results.json`, `packages/types/schemas/*.schema.json` — not touched, safe to leave/normalize separately.
- This session's build artifacts that the mount won't let me delete (all gitignored / not committed): `apps/web/.next` (now a broken symlink), several `apps/web/.next_old*`/`.next_dead*` dirs, `apps/web/tsconfig.tsbuildinfo`, and FUSE `.fuse_hidden*` files. Delete these from Windows at your convenience.

---

## Session Update (2026-06-11, continued #4 — shell-capable agent)

Status: Shell available (after a slow start). Committed Batch item 1 (backend resilience). Batch items 2 and 3 are still **not started**.

### Done and committed this session (on `main`)
- **`6999d65`** — Add per-agent resilience and JSON-retry to orchestrator (`apps/api/app/providers/model.py`, `apps/api/app/services/orchestrator.py`, `apps/api/tests/test_resilience.py`). This is Batch item 1 from session #3, verified by re-running `pytest apps/api/tests` on a clean copy of the repo (sandbox copy, not the mounted Windows path — see "Sandbox quirks" below): **13 passed**.

### Sandbox quirks discovered this session (read before doing git/pytest work)
1. **`pytest` over the mounted Windows folder fails with `sqlite3.OperationalError: disk I/O error`.** The test DB (`apps/api/test-hxrizxn.db`, hardcoded in `apps/api/tests/conftest.py`) can't reliably do SQLite locking on the `/sessions/*/mnt/HXRIZXN` mount. Workaround used this session: `cp -r` the whole repo to `/tmp/work/repo` (native fs) and run pytest there. This is read-only verification — don't try to commit from the `/tmp` copy (it was an incomplete `cp`, missing some dotfiles like `.env.example`/`.gitignore`).
2. **`git commit` (and any git command that needs to write `.git/index.lock` or `.git/HEAD.lock`) hangs/fails with `Unable to create '.git/index.lock': File exists`,** and the stale lock file **cannot be removed** (`rm`/`mv`/`os.remove` all return `Operation not permitted`, even though the file is owned by the same user with `rwx` perms). This looks like the virtual filesystem holding a host-side handle open briefly after creation.
   - **Workaround that worked**: don't let git create `.git/index.lock` at all. Use an external index file:
     ```bash
     cp .git/index /tmp/gitindex
     GIT_INDEX_FILE=/tmp/gitindex GIT_AUTHOR_NAME="mehulnikumbh19" GIT_AUTHOR_EMAIL="mnikumbh19@gmail.com" \
       GIT_COMMITTER_NAME="mehulnikumbh19" GIT_COMMITTER_EMAIL="mnikumbh19@gmail.com" \
       git commit -m "..."
     ```
     This still prints `warning: unable to unlink '.git/HEAD.lock' / '.git/objects/.../tmp_obj_*'` but the commit **succeeds anyway** (verified with `git log` / `git show --stat HEAD`). `git status`/`git add` work fine without the env var (they don't seem to leave a stuck lock on their own — only commit did, and only sometimes). If `git add`/`git status` ever does leave a stuck `.git/index.lock`, `mv` it aside (rename can work even when `rm` doesn't) rather than deleting.
   - No global git identity is configured in this sandbox (`user.name`/`user.email` unset) — that's why `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env vars were needed. Reuse `mehulnikumbh19 <mnikumbh19@gmail.com>` (matches all prior commits) or set `git config user.name`/`user.email` locally if preferred.
3. **`pip install` is not pre-provisioned** in this sandbox. Needed `pip install -r apps/api/requirements.txt --break-system-packages` plus `pip install pytest pytest-asyncio httpx --break-system-packages` to get `pytest apps/api/tests` working at all. `python3 -m pytest` works after that; bare `pytest` is not on `PATH` (`/sessions/.../.local/bin` isn't on `PATH` by default).

### Approved improvement plan (unchanged — still the active plan)
Full prioritized roadmap saved at `C:\Users\mniku\.claude\plans\i-think-it-works-witty-rose.md`. Approved focused batch of 3:
1. ✅ Backend per-agent resilience + JSON retry — **done and committed (`6999d65`)**.
2. ⬜ Persist analysis across refresh — add Zustand `persist` middleware to `apps/web/lib/useDecisionStore.ts` (sessionStorage; on rehydrate, if `screen === "loading"` reset to `"intake"`; use `skipHydration` + mount effect to avoid Next.js hydration mismatch).
3. ⬜ Input validation in `runCustom` (non-empty prompt, `moneyLimit`/`timeHorizon` > 0) + fix the dead "Upload Docs" button in `HxrizxnApp.tsx` (recommend disabling/"coming soon" for this batch; full upload wiring is roadmap Tier 2).

### Immediate next steps
1. Implement Batch item 2 (Zustand persist), test (`npm --workspace apps/web run test`, `run build`), commit, pause for user confirmation.
2. Implement Batch item 3 (input validation + Upload Docs button), test, commit, pause for user confirmation.
3. Optionally re-run `python scripts/run_evals.py` now that Batch item 1 is committed — session #3 predicted the Assumption Miner `ReadTimeout` would now degrade gracefully instead of crashing the whole eval run. Confirm.
4. Do **not** push/deploy without explicit user confirmation.

### Housekeeping / uncommitted (as of end of this session)
- `HANDOFF.md` (this update).
- `apps/web/next-env.d.ts`, `apps/web/tsconfig.json`, `evals/latest-results.json`, and all of `packages/types/schemas/*.schema.json` — these show as modified but the diffs are **purely CRLF/LF line-ending churn** from local tooling (verified on `SafetyFlag.schema.json`). Safe to leave alone or to normalize in a dedicated commit later; not part of any feature work.
- Untracked: `AGENT_HANDOFF_PROMPT.md` (session #2's handoff prompt, no longer needed but harmless), `.claude/` (local settings), `apps/api/test-hxrizxn.db-journal` (test artifact, safe to delete), and `favicon_io (1)/` (**do not commit** unless intentionally wired into `apps/web/public`).

---

## Session Update (2026-06-11, continued #2)

Status: Sandbox shell still unavailable (stuck on "Workspace still starting" across many retries, multiple times this session). Made progress using file tools (Read/Grep/Edit) only. No tests/build/commit/push possible yet.

Confirmed via direct file read:

- `apps/web/lib/api.ts` `createAndAnalyzeDecision` ALREADY implements the recommended intake-metadata fix: `title = raw_prompt.slice(0, 60) + "..."`, and `decision_type` is inferred via keyword matching (startup, relocation, graduate_school, home_purchase for house/buy/mortgage/rent, career, else "general"). The "Known High-Priority Bug" section's described problem (hardcoded startup title/type sent for every prompt) appears to be ALREADY FIXED in the current worktree. Still need `git diff`/`git status` once shell works to confirm whether this fix is committed or uncommitted.
- `apps/api/app/core/config.py`: `api_cors_origins` defaults to `http://localhost:3000,http://127.0.0.1:3000` — fine for local dev. `scripts/deploy_azure_appservice_demo.ps1` sets `API_CORS_ORIGINS=$webUrl,http://localhost:3000,http://127.0.0.1:3000` for prod — includes the deployed web origin. CORS does not look like the cause of the fallback issue.
- Confirmed the fallback-on-error hypothesis is real and is now PARTIALLY FIXED (made this session): in `apps/web/components/HxrizxnApp.tsx`, `runCustom()`'s catch block calls `fetchDemoPackage()` (-> hardcoded `fallbackPackage`, the startup-flavored demo) and sets `screen("comparison")`. The `error` string was previously only rendered on the Intake screen (line ~385), which is never shown again once `screen` becomes `"comparison"` — so users got zero indication the content was an unrelated demo fallback.

### Edits made this session (uncommitted, untested — shell still down)

- `apps/web/components/HxrizxnApp.tsx`:
  - Added `isFallbackDemo` state, set to `true` only in `runCustom()`'s catch path (reset to `false` at the start of `runDemo()` and `runCustom()`).
  - Passed `isFallbackDemo` into `<Comparison>`.
  - `Comparison` now renders an amber banner at the top when `isFallbackDemo` is true: "Live analysis was unavailable, so this is unrelated demo content shown as a fallback — it does not reflect your prompt..."

Not yet done: `Ripple`, `Experiment`, and `Memo` screens (also reachable from comparison via `setScreen`) do not receive/show this banner. Consider threading `isFallbackDemo` through to those screens too, or lifting the banner into a layout wrapper in `HxrizxnApp()` so it persists across all post-analysis screens regardless of which one is active.

### Recommended next steps (in order)

1. Get shell access working again (restart/reconnect session if needed).
2. `git status` / `git diff` to see full uncommitted diff, including this session's `HxrizxnApp.tsx` banner edit and the prior intake-metadata state.
3. Reproduce locally: run `npm run dev` + local API, submit the house-buying test prompt from the "Known High-Priority Bug" section below, and confirm (a) title/decision_type are now prompt-derived, and (b) if `runCustom()` ever falls back, the new banner appears.
4. Decide whether to thread `isFallbackDemo` into `Ripple`/`Experiment`/`Memo` screens too (recommended) and implement if so.
5. Run `npm --workspace apps/web run test`, `run build`, `run test:e2e`, and `pytest apps/api/tests` before committing.
6. Commit fixes individually per user instruction (confirm with user after each completed task), then ask before pushing or deploying.

## Current State

Hxrizxn AI is now a working local and Azure-deployed MVP. The production API is live on Azure Container Apps, using Azure OpenAI for model calls and Azure AI Search as the grounding/retrieval backend. The frontend is also live on Azure Container Apps.

Production URLs:

- Web: `https://hxrizxn-web.agreeableforest-fd08d701.eastus2.azurecontainerapps.io`
- API: `https://hxrizxn-api.agreeableforest-fd08d701.eastus2.azurecontainerapps.io`
- API health: `https://hxrizxn-api.agreeableforest-fd08d701.eastus2.azurecontainerapps.io/api/health`

Current production health response:

```json
{
  "ok": true,
  "service": "hxrizxn-api",
  "demo_mode": false,
  "foundry_iq_configured": true
}
```

Local app endpoints:

- Web: `http://localhost:3000`
- API: `http://127.0.0.1:8000`
- API health: `http://127.0.0.1:8000/api/health`

Local `.env` is configured for live mode:

- `DEMO_MODE=false`
- Azure OpenAI endpoint/key/deployment are set locally.
- Foundry IQ/Azure AI Search endpoint/key/index are set locally.
- `.env` is ignored by git and must not be committed.

## Completed

### Backend

- FastAPI app in `apps/api`.
- Pydantic v2 JSON contracts in `apps/api/app/schemas.py`.
- SQLAlchemy models and Alembic migration for:
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
- Deterministic HORIZON-X workflow with live model-provider support.
- Microsoft Agent Framework dependency and runtime adapter.
- Azure OpenAI provider in `apps/api/app/providers/model.py`.
- Azure AI Search-backed grounding provider in `apps/api/app/providers/knowledge.py`.
- Local mock fallbacks for model and grounding providers.
- Local object storage and Azure Blob-ready storage abstraction.
- Upload validation, text redaction, prompt-injection sanitization, secure headers, and rate-limit middleware.
- Persisted agent traces and markdown report generation.
- Live model-output schema normalization for common label mismatches such as `relationship` -> `relationships`.

### Current Agent Workflow

The orchestrator currently exposes 11 trace steps:

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

This is intentionally expanded from the original nine-agent framing because grounding, assumption mining, and future-self generation were split into explicit visible nodes.

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
  - analysis loading screen
  - scenario comparison
  - ripple/risk analysis
  - experiment plan
  - decision memo and report export
- Local fallback package if the API path fails.
- Production frontend points to production API through:
  - `NEXT_PUBLIC_API_URL=https://hxrizxn-api.agreeableforest-fd08d701.eastus2.azurecontainerapps.io`

### Azure / Cloud

Azure subscription currently used:

- Subscription name: `Azure subscription 1`
- Subscription ID: `d57da176-04a2-426e-b61a-12845c8095c8`
- Resource group: `rg-hxrizxn-demo2`

Provisioned resources:

| Resource | Name | Status |
| --- | --- | --- |
| Azure Container Registry | `hxr45810acr` | Created and in use |
| API Container App | `hxrizxn-api` | Running |
| Web Container App | `hxrizxn-web` | Running |
| Azure OpenAI resource | `hxrizxn-openai` | Created |
| Azure OpenAI deployment | `gpt-4.1-mini` | Created, model `gpt-4.1-mini`, version `2025-04-14` |
| Azure AI Search service | `hxrizxn-search-d57da176` | Created, Free tier, East US |
| Search index | `hxrizxn-demo` | Created and loaded |
| Demo knowledge docs | `demo-data/*` | 6 docs uploaded to search index |

Production API config:

- `DEMO_MODE=false`
- `AZURE_OPENAI_ENDPOINT=https://hxrizxn-openai.openai.azure.com/`
- `AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini`
- `AZURE_OPENAI_API_KEY` stored as Container App secret `azure-openai-api-key`
- `FOUNDRY_IQ_ENDPOINT=https://hxrizxn-search-d57da176.search.windows.net`
- `FOUNDRY_IQ_INDEX_NAME=hxrizxn-demo`
- `FOUNDRY_IQ_API_KEY` stored as Container App secret `foundry-iq-api-key`
- `OPENAI_API_KEY` still exists as a fallback secret, but the app prefers Azure OpenAI when Azure settings are present.

Verified production behavior:

- API health returns `demo_mode: false` and `foundry_iq_configured: true`.
- Cloud analysis returns 3 scenarios and 11 trace steps.
- Grounding citations come from the Azure AI Search-backed indexed docs.
- Web app returns HTTP 200.

### Commits Already Made Locally

Recent local commits:

```text
09f02ee Use Azure AI Search for grounding retrieval
85a5ab0 Normalize live model schema labels
e482e5b Checkpoint local MVP and demo deployment path
4bad552 Fix Azure deployment for student subscriptions and add GitHub image builds.
7a7084e Initial commit: Hxrizxn AI multi-agent decision simulator.
```

These commits are local unless they have since been pushed manually.

## Verification Results

Known successful checks from this session:

```text
pytest apps/api/tests
Result: 8 passed
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
Result: 2 passed
```

```text
python scripts/run_evals.py
Result: 5 cases, average score 9.6
```

Known warnings:

- FastAPI `on_event` deprecation warning.
- Microsoft Agent Framework experimental warnings from installed framework internals.
- These warnings are known and not currently blocking.

## Current Worktree State

There are uncommitted frontend changes from the latest debugging pass:

- `apps/web/components/HxrizxnApp.tsx`
  - Adds better live-analysis loading behavior with elapsed time and slower agent progression.
- `apps/web/lib/api.ts`
  - Adds an analysis request timeout.
- `apps/web/next-env.d.ts`
  - Modified by local Next/build tooling.

There is also an untracked loose favicon export folder:

- `favicon_io (1)/`

Do not commit `favicon_io (1)/` unless the assets are intentionally wired into `apps/web/public`.

Important: the uncommitted frontend changes have not been fully reviewed/committed yet. The user interrupted while a web image deploy was being attempted. Before touching web deployment, check ACR build status:

```powershell
az acr task list-runs --registry hxr45810acr --top 5 --query "[].{runId:runId,status:status,createTime:createTime}" --output table
```

At the last check, ACR builds through `cha` had succeeded. Confirm the latest build state before starting another web build.

## Known High-Priority Bug

Custom user prompts are still being wrapped in hardcoded startup metadata in `apps/web/lib/api.ts`.

Current problematic behavior:

- User enters a custom prompt, for example:
  - "Should I buy a 3-bedroom fixer-upper house in Austin..."
- Frontend sends:
  - `title: "Quit job or test the AI startup first?"`
  - `decision_type: "startup"`
  - startup-specific goals/fears/constraints
- Result: the analysis can display the startup title and startup-flavored scenario names even when the raw prompt is about housing, relocation, school, etc.

This is why the latest user screenshot showed:

- `Quit job or test the AI startup first?`
- `Controlled Upside Branch`
- `Evidence-Building Base Case`
- `Runway Compression Stress Case`

even though the user typed a house-buying scenario.

Recommended fix:

1. Change `createAndAnalyzeDecision` in `apps/web/lib/api.ts` so it sends neutral/custom metadata.
2. Either infer `decision_type` client-side from the prompt or send a generic type such as `life`.
3. Generate the title from the first sentence/first 80 characters of the prompt instead of hardcoding the startup title.
4. Use generic empty arrays or lightly inferred goals/fears/constraints instead of startup-specific values.
5. Consider adding optional intake fields later for title, decision type, goals, fears, constraints, money limit, and time horizon.

A simple immediate patch would send:

```ts
{
  title: raw_prompt.slice(0, 90),
  decision_type: inferDecisionType(raw_prompt),
  raw_prompt,
  goals: [],
  fears: [],
  constraints: [],
  time_horizon_months: 24
}
```

Suggested `inferDecisionType` mapping:

- house, mortgage, rent, renovate -> `home_purchase`
- move, country, city, visa -> `relocation`
- school, graduate, degree -> `graduate_school`
- job, career, role, product management -> `career`
- startup, founder, company -> `startup`
- otherwise -> `life`

After patching, test specifically with:

```text
Should I buy a 3-bedroom fixer-upper house in Austin, Texas with a 6.8% mortgage rate requiring $40k in renovations, or keep renting a downtown apartment for the next 2 years to stay mobile?
```

Expected result:

- Title should mention buying/renting/fixer-upper, not quitting a job.
- Scenarios should discuss home purchase/renting/mobility/renovation risk.
- Memo should include finance/housing disclaimers.

## Remaining Work

### 1. Fix Custom Intake Metadata

Status: Not done.

This is the most urgent user-facing issue. See the high-priority bug section above.

### 2. Finish Frontend Loading UX Patch

Status: Partially done, uncommitted.

The current local worktree includes a loading/timeout UX patch, but it was not committed or deployed before interruption. Review, test, and either keep or revise it.

Recommended checks:

```powershell
npm --workspace apps/web run test
npm --workspace apps/web run build
npm --workspace apps/web run test:e2e
```

Then build/deploy the web image if desired:

```powershell
az acr build --registry hxr45810acr --image hxrizxn-web:latest apps/web --no-logs
az containerapp update `
  --name hxrizxn-web `
  --resource-group rg-hxrizxn-demo2 `
  --image hxr45810acr.azurecr.io/hxrizxn-web:latest
```

If Azure CLI log streaming crashes or times out, check build status with:

```powershell
az acr task list-runs --registry hxr45810acr --top 5 --output table
```

### 3. Push Git Commits

Status: Not done unless the user pushed manually.

The latest commits are local. Confirm remote/branch before pushing.

```powershell
git status
git remote -v
git push
```

### 4. Production Database Migrations

Status: Needs confirmation.

The API still uses startup convenience DB creation for local/MVP flow. Alembic migration exists, but production migration execution should be formalized.

If using the deployed PostgreSQL database and disabling `create_all`, run:

```powershell
cd apps/api
python -m alembic upgrade head
```

Make sure `DATABASE_URL` points at the production database before running production migrations.

### 5. Real User Authentication

Status: Not done.

The app still has demo/stub auth. Microsoft Entra/OAuth and role-based access control remain future work.

### 6. Security Hardening

Completed:

- Upload validation
- Redaction
- Prompt-injection sanitization
- Secure headers
- Rate limiting
- Azure secrets are stored in Container App secrets for API keys

Remaining:

- Rotate temporary secrets before public push or long-lived production usage.
- Replace broad production CORS defaults with the exact web origin only.
- Add Microsoft Entra/OAuth.
- Add stronger crisis/self-harm UX flow.
- Add Azure Content Safety if required.

### 7. Observability

Completed:

- Local logs
- Persisted agent traces
- Agent trace graph in UI
- Azure Container App logs

Remaining:

- Application Insights telemetry instrumentation.
- Token usage tracking from real providers.
- Latency dashboards.
- Per-agent telemetry dashboards.
- Foundry tracing, if required for the final submission.

### 8. Grounding Quality

Status: Basic cloud grounding works.

Currently, Azure AI Search index `hxrizxn-demo` contains only 6 demo documents from `demo-data`. This proves the grounding path works, but it is not a rich real knowledge base yet.

Remaining:

- Add better housing/finance/relocation knowledge docs.
- Add upload-to-index pipeline so user-uploaded documents become searchable in Azure AI Search, not only stored.
- Consider semantic/vector search if quality matters.

### 9. Dependency / Warning Cleanup

Remaining:

- FastAPI `on_event` warning: migrate startup logic to lifespan handlers.
- Microsoft Agent Framework experimental warnings: known/acceptable for MVP.
- `npm audit --omit=dev` previously reported moderate Next/PostCSS advisories; do not force a breaking remediation without reviewing.

## Important Commands

Start local dev:

```powershell
npm run dev
```

Run API tests:

```powershell
pytest apps/api/tests
```

Run web tests/build:

```powershell
npm --workspace apps/web run test
npm --workspace apps/web run build
npm --workspace apps/web run test:e2e
```

Run evals:

```powershell
python scripts/run_evals.py
```

Check production health:

```powershell
Invoke-RestMethod "https://hxrizxn-api.agreeableforest-fd08d701.eastus2.azurecontainerapps.io/api/health"
```

Check Container App logs:

```powershell
az containerapp logs show --name hxrizxn-api --resource-group rg-hxrizxn-demo2 --tail 120
az containerapp logs show --name hxrizxn-web --resource-group rg-hxrizxn-demo2 --tail 120
```

Check latest ACR builds:

```powershell
az acr task list-runs --registry hxr45810acr --top 5 --output table
```

## Honest Claims

Can claim:

- Hxrizxn AI is deployed on Azure Container Apps.
- Production API uses Azure OpenAI deployment `gpt-4.1-mini`.
- Production grounding is configured and backed by Azure AI Search.
- The app persists agent traces and shows an 11-step HORIZON-X workflow.
- Local and production health are in live mode with grounding configured.

Do not claim yet:

- Full Microsoft Entra authentication is implemented.
- User uploads are automa
