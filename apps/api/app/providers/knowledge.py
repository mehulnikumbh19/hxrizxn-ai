from __future__ import annotations

from dataclasses import dataclass

import httpx

from app.core.config import Settings
from app.schemas import Citation


@dataclass(frozen=True)
class RetrievalQuery:
    case_id: str | None
    query: str
    decision_type: str
    top_k: int = 4


class KnowledgeProvider:
    name = "base"

    def retrieve(self, query: RetrievalQuery) -> list[Citation]:
        raise NotImplementedError


class MockKnowledgeProvider(KnowledgeProvider):
    name = "mock"

    _docs = [
        Citation(
            title="Decision Science Brief",
            source="demo-data/decision-science-brief.md",
            snippet="Use reversible experiments to reduce uncertainty before one-way-door commitments.",
            confidence="high",
        ),
        Citation(
            title="Startup Burn Rate Note",
            source="demo-data/startup-idea-note.md",
            snippet="Founder risk is dominated by runway, customer evidence, isolation, and execution cadence.",
            confidence="high",
        ),
        Citation(
            title="Personal Budget",
            source="demo-data/current-monthly-budget.csv",
            snippet="Eight months of savings creates room for testing, but full-time exploration increases burn risk.",
            confidence="medium",
        ),
        Citation(
            title="Relocation and School Planning Note",
            source="demo-data/relocation-grad-school-note.md",
            snippet="Large moves deserve attention to visa, social support, cost of living, and exit paths.",
            confidence="medium",
        ),
    ]

    def retrieve(self, query: RetrievalQuery) -> list[Citation]:
        terms = {term.lower().strip(".,!?") for term in query.query.split() if len(term) > 3}
        scored: list[tuple[int, Citation]] = []
        for doc in self._docs:
            text = f"{doc.title} {doc.snippet}".lower()
            score = sum(1 for term in terms if term in text)
            if query.decision_type.lower() in text:
                score += 1
            scored.append((score, doc))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for _, doc in scored[: query.top_k]]


class FoundryIQKnowledgeProvider(KnowledgeProvider):
    name = "foundry-iq"

    def __init__(self, settings: Settings):
        self.settings = settings

    def retrieve(self, query: RetrievalQuery) -> list[Citation]:
        if not self.settings.foundry_iq_configured:
            return []
        payload = {
            "index": self.settings.foundry_iq_index_name,
            "query": query.query,
            "top_k": query.top_k,
            "filters": {"case_id": query.case_id, "decision_type": query.decision_type},
        }
        headers = {"api-key": self.settings.foundry_iq_api_key or ""}
        try:
            response = httpx.post(
                f"{self.settings.foundry_iq_endpoint.rstrip('/')}/query",
                json=payload,
                headers=headers,
                timeout=8,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return []
        data = response.json()
        citations: list[Citation] = []
        for item in data.get("results", [])[: query.top_k]:
            citations.append(
                Citation(
                    title=item.get("title", "Foundry IQ result"),
                    source=item.get("source", "Foundry IQ"),
                    snippet=item.get("snippet", ""),
                    confidence=item.get("confidence", "medium"),
                )
            )
        return citations


def get_knowledge_provider(settings: Settings) -> KnowledgeProvider:
    if settings.foundry_iq_configured:
        return FoundryIQKnowledgeProvider(settings)
    return MockKnowledgeProvider()

