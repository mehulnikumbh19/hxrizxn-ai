# Evaluations

The eval harness lives in `scripts/run_evals.py` and uses `evals/golden_cases.json`.

It scores:

- Structure completeness
- Scenario diversity
- Second-order coverage
- Recommendation usefulness
- Safety compliance
- Scenario and memo consistency
- Citation presence
- Required keyword coverage

Run:

```bash
python scripts/run_evals.py
```

Output is written to `evals/latest-results.json`.

