# Safety

Hxrizxn AI is decision support, not a licensed professional.

## Rules

- Never claim certainty for life outcomes.
- Use probability bands instead of fake exact percentages.
- Detect high-stakes domains: medical, legal, mental health crisis, immigration/legal compliance, and large financial decisions.
- For high-stakes domains, add disclaimers and recommend qualified professional consultation when appropriate.
- Block or safely redirect self-harm, violence, or illegal assistance requests.
- Keep traces transparent without exposing chain-of-thought.

## Technical Controls

- Pydantic schemas validate every agent output.
- `Verifier and Safety Agent` checks scenario coverage, risk coverage, experiment reversibility, and safety flags.
- Upload type restrictions protect document ingestion.
- Prompt injection sanitizer removes retrieved instruction-like strings.
- Redaction helper masks email, SSN-like values, and card-like numbers.
- Secure headers and rate-limit middleware are enabled.

