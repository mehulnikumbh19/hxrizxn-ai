from __future__ import annotations

from app.schemas import SafetyFlag


HIGH_STAKES_TERMS = {
    "medical": ["diagnosis", "medicine", "surgery", "symptom", "doctor", "hospital"],
    "legal": ["lawsuit", "contract", "sue", "court", "criminal", "lawyer"],
    "immigration/legal compliance": ["visa", "immigration", "deport", "asylum", "work permit"],
    "large financial decision": ["mortgage", "house", "debt", "loan", "invest", "crypto", "stock"],
    "mental health crisis": ["suicide", "self harm", "self-harm", "kill myself", "hopeless"],
    "illegal assistance": ["fake documents", "evade tax", "launder", "hack into", "steal"],
    "violence": ["hurt someone", "weapon", "attack them", "revenge"],
}


def detect_safety_flags(text: str) -> list[SafetyFlag]:
    lowered = text.lower()
    flags: list[SafetyFlag] = []
    for domain, terms in HIGH_STAKES_TERMS.items():
        if any(term in lowered for term in terms):
            severity = "caution"
            boundary = "Keep the output as decision support and recommend a qualified professional where appropriate."
            if domain in {"mental health crisis", "illegal assistance", "violence"}:
                severity = "block"
                boundary = "Do not provide operational assistance; provide safe redirection and emergency resources if relevant."
            flags.append(
                SafetyFlag(
                    domain=domain,
                    severity=severity,
                    message=f"Detected high-stakes domain: {domain}.",
                    recommended_boundary=boundary,
                )
            )
    return flags


def default_disclaimer(flags: list[SafetyFlag]) -> str:
    base = "Hxrizxn AI is decision support, not a licensed professional."
    if not flags:
        return base
    domains = ", ".join(sorted({flag.domain for flag in flags}))
    return f"{base} This case touches {domains}; consult a qualified professional before acting."

