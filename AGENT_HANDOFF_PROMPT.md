# Prompt for next agent (shell-capable)

Paste everything below to the other agent/LLM. It has full context on what's done and what's left.

---

You're picking up work on **Hxrizxn AI**, a multi-agent decision-simulator app (Next.js frontend in `apps/web`, FastAPI backend in `apps/api`), deployed to Azure Container Apps. The repo root has a `HANDOFF.md` with full project history — read it first for background (Azure resource names, env vars, architecture, etc.). This prompt covers only the **current task**: fixing a frontend bug and verifying everything still works.

## Why you're here

The previous agent (me) had no working shell/sandbox all session, so I could only read and edit files — no `git`, `npm`, `pytest`, or builds were run. You have shell access, so your job is to verify, test, and commit what I changed.

## What's already been confirmed/done (via file reads/edits only, NOT tested)

### 1. Intake metadata bug — appears already fixed
File: `apps/web/lib/api.ts`, function `createAndAnalyzeDecision`.

Previously this function hardcoded a "Quit job or test the AI startup first?" title and `decision_type: "startup"` for every prompt, even house-buying prompts. Reading the current file shows this is **already fixed**:
- `title = raw_prompt.slice(0, 60) + (raw_prompt.length > 60 ? "..." : "")`
- `decision_type` is inferred from keywords in `raw_prompt.toLowerCase()`:
  - `quit`/`startup`/`founder` -> `startup`
  - `move`/`country`/`relocat` -> `relocation`
  - `school`/`grad`/`degree` -> `graduate_school`
  - `house`/`buy`/`mortgage`/`rent` -> `home_purchase`
  - `career`/`job`/`switch` -> `career`
  - else -> `general`

**You need to confirm**: is this fix already committed, or is it part of the uncommitted worktree changes? Run `git status` and `git diff -- apps/web/lib/api.ts` against `HEAD` to find out. If uncommitted, it needs review + tests + commit per the steps below.

### 2. CORS — checked, looks fine
- `apps/api/app/core/config.py`: `api_cors_origins` defaults to `http://localhost:3000,http://127.0.0.1:3000`.
- `scripts/deploy_azure_appservice_demo.ps1` sets `API_CORS_ORIGINS=$webUrl,http://localhost:3000,http://127.0.0.1:3000` for prod, which includes the deployed web app's own URL.
- Conclusion: CORS is not the cause of the fallback-to-demo issue. No action needed here unless your testing proves otherwise.

### 3. Fallback-to-demo UX bug — root cause confirmed, partial fix made (UNCOMMITTED, UNTESTED)
File: `apps/web/components/HxrizxnApp.tsx`.

**Root cause**: `runCustom()` calls the live API (`createAndAnalyzeDecision`). If that throws for ANY reason (network error, timeout, 4xx/5xx, etc.), the `catch` block calls `fetchDemoPackage()`, which can return the hardcoded `fallbackPackage` from `apps/web/lib/api.ts` — a fictional "Quit job or test the AI startup first?" scenario with startup-flavored scenario names ("Controlled Upside Branch", "Evidence-Building Base Case", "Runway Compression Stress Case"). The screen then transitions to `"comparison"` and shows this fake content. An `error` string was set, but it was only ever rendered on the **Intake** screen (a `useState` checked at line ~385 of the original file), which the user never sees again once the screen switches to `"comparison"`. Result: users could see completely unrelated "startup" demo content with no indication it's a fallback.

**My fix (uncommitted, in current worktree, NOT YET TESTED)**:
- Added `const [isFallbackDemo, setIsFallbackDemo] = useState(false);` near the other state in `HxrizxnApp()`.
- `runDemo()` and the start of `runCustom()` set `setIsFallbackDemo(false)`.
- `runCustom()`'s catch block sets `setIsFallbackDemo(true)` right where it falls back to `fetchDemoPackage()`.
- Passed `isFallbackDemo={isFallbackDemo}` into `<Comparison data={packageData} setScreen={setScreen} isFallbackDemo={isFallbackDemo} />`.
- `Comparison` component signature now accepts `isFallbackDemo?: boolean` and, when true, renders an amber warning banner at the top of the screen:
  > "Live analysis was unavailable, so this is unrelated demo content shown as a fallback — it does not reflect your prompt. Try again in a moment, or check your connection to the API."

**Known gap / open decision for you**: The `Ripple`, `Experiment`, and `Memo` screens (also reachable from `Comparison` via `setScreen`, all rendered in the same `HxrizxnApp()` return block around line 184-187) do **not** receive or show this banner. If a user navigates from Comparison to Ripple/Experiment/Memo while in fallback mode, the warning disappears. Two options:
  - (a) Thread `isFallbackDemo` into those three components too (same pattern as `Comparison`), or
  - (b) Lift the banner into a persistent layout element in `HxrizxnApp()`'s main return, above the `{screen === ...}` conditionals, so it shows regardless of which post-analysis screen is active.

Pick whichever is cleaner given the actual component structure — (b) is probably less repetitive. Implement it.

### 4. Other known uncommitted changes (from before this session, not yet reviewed by anyone with a shell)
- `apps/web/lib/api.ts` — added an `ANALYSIS_TIMEOUT_MS = 210_000` request timeout via `fetchWithTimeout`/`AbortController` for the `/analyze` call.
- `apps/web/components/HxrizxnApp.tsx` — loading screen now tracks elapsed time (`loadingElapsedSec`) and cycles through agent labels every 10s (`startLoadingSequence`/`agentLabels`).
- `apps/web/next-env.d.ts` — likely just regenerated by Next tooling, probably fine to leave/ignore or regenerate.
- Untracked loose folder `favicon_io (1)/` at repo root — **do not commit this** unless its assets are intentionally wired into `apps/web/public`. If unused, consider deleting it (confirm with user first) or leaving it untracked/gitignored.

## Your task, in order

1. **Orient**: `cd` to repo root, run `git status` and `git diff` (and `git diff --stat` for an overview). Read `HANDOFF.md` for full project context. Cross-reference the diff against sections 1, 3, and 4 above so you know exactly what's already changed vs. what you still need to do.

2. **Implement the remaining fallback-banner work** (section 3's "known gap"): extend the fallback warning to `Ripple`, `Experiment`, and `Memo` screens, or lift it to a shared layout location. Keep styling consistent with the existing amber banner (`border border-amber-300/40 bg-amber-300/10 text-amber-100`, rounded, padded).

3. **Manual repro test** (requires local dev servers):
   - Start the local API (`http://127.0.0.1:8000`) and web app (`npm run dev`, `http://localhost:3000`). Confirm `.env` is configured for live mode (`DEMO_MODE=false`, Azure OpenAI + Foundry IQ vars set) per `HANDOFF.md`.
   - In the UI, submit this exact test prompt via "Open Intake" -> "Analyze Decision":
     ```
     Should I buy a 3-bedroom fixer-upper house in Austin, Texas with a 6.8% mortgage rate requiring $40k in renovations, or keep renting a downtown apartment for the next 2 years to stay mobile?
     ```
   - **Expected on success**: title mentions buying/renting/fixer-upper (not "Quit job..."), scenarios discuss home purchase/renting/mobility/renovation risk, memo includes finance/housing disclaimers, no fallback banner shown.
   - **If it falls back anyway**: confirm the new amber banner appears on Comparison (and on whichever screen you navigate to next, per step 2's fix). Capture the actual error message shown (it includes the underlying error detail) and investigate the real cause (check API logs, network tab, `/api/cases` and `/api/cases/{id}/analyze` responses) — this is a secondary bug to flag/fix if found, separate from the UX-banner fix.

4. **Run the full test suite**:
   ```
   pytest apps/api/tests
   npm --workspace apps/web run test
   npm --workspace apps/web run build
   npm --workspace apps/web run test:e2e
   python scripts/run_evals.py
   ```
   All of these passed previously (8 passed / 1 passed / build passed / 2 passed / avg score 9.6) — any new failures should be investigated before committing.

5. **Commit**, but **one logical change at a time**, and **stop and ask the user for confirmation after each commit** before doing the next one. Suggested commit breakdown:
   - Commit A: intake-metadata fix in `apps/web/lib/api.ts` (if not already committed).
   - Commit B: loading UX patch (`HxrizxnApp.tsx` elapsed time / agent label cycling) + analysis timeout (`api.ts`).
   - Commit C: fallback-demo banner fix (this session's `isFallbackDemo` work + your extension to Ripple/Experiment/Memo).
   - Do **not** commit `favicon_io (1)/` unless the user confirms it should be wired in.

6. **Do not push or deploy** (`git push`, `az acr build`, `az containerapp update`, etc.) without explicit user confirmation — ask after all commits are made and tests pass.

## Constraints / house rules

- Never commit `.env` (already gitignored).
- Don't touch Azure resources/deploys without asking first.
- If you find the live API call is genuinely failing (not just a UX issue), report the root cause clearly before attempting a fix — don't silently patch around it.
- Keep changes scoped; don't refactor unrelated code.

## Reference: key files

- `apps/web/lib/api.ts` — API client, intake metadata mapping, demo/fallback package.
- `apps/web/components/HxrizxnApp.tsx` — main app component, screens, fallback logic.
- `apps/api/app/main.py`, `apps/api/app/core/config.py` — FastAPI app, CORS config.
- `HANDOFF.md` — full project history, Azure resource details, completed/remaining work tracker.
