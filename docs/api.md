# API

Base URL: `http://localhost:8000`.

## Routes

- `GET /api/health`: service status and Foundry IQ configuration state.
- `POST /api/cases`: create a decision case.
- `GET /api/cases/{id}`: fetch a case.
- `POST /api/cases/{id}/analyze`: run HORIZON-X.
- `GET /api/cases/{id}/scenarios`: fetch persisted scenarios.
- `GET /api/cases/{id}/trace`: fetch agent traces.
- `POST /api/cases/{id}/documents`: upload grounding documents.
- `GET /api/cases/{id}/report`: printable Markdown report.
- `GET /api/demo/scenarios`: seeded demo analysis.

## Example

```bash
curl -X POST http://localhost:8000/api/cases \
  -H "Content-Type: application/json" \
  -d '{"decision_type":"startup","raw_prompt":"Should I quit my job and start a startup or test part-time first?"}'
```

JSON schemas can be exported with:

```bash
python scripts/export_schemas.py
```

