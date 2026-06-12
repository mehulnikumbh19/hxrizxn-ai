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
    top_k: int = 6


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
        Citation(
            title="Enterprise Contract Playbook",
            source="demo-data/enterprise-contract-playbook.md",
            snippet="A large enterprise contract with custom feature requirements can generate significant annual revenue, but projected revenue rarely lands in full within the first 18-month horizon; phase the contract and tie payment to delivered milestones.",
            confidence="high",
        ),
        Citation(
            title="Engineering Capacity and Roadmap Note",
            source="demo-data/engineering-capacity-note.md",
            snippet="Custom feature work for one customer pulls engineering capacity off the core roadmap and commonly causes a multi-month delay; protect team capacity and morale with explicit prioritization, or risk burnout and attrition.",
            confidence="high",
        ),
        Citation(
            title="Customer Concentration Risk Brief",
            source="demo-data/customer-concentration-brief.md",
            snippet="Over-reliance on a single large enterprise customer as a proof point or reference is fragile: sudden large customer churn, refusal to phase features, or a backfiring reference can undermine future sales and revenue.",
            confidence="high",
        ),
        Citation(
            title="Revenue and Runway Model",
            source="demo-data/revenue-runway-model.md",
            snippet="When partial revenue falls short of financial needs, runway compresses fast; define a cash floor, a weekly burn review, and an automatic stop condition before committing to a deal or one-way-door step.",
            confidence="high",
        ),
        Citation(
            title="Engineering Burnout and Attrition Note",
            source="demo-data/engineering-burnout-note.md",
            snippet="Even with effective prioritization, sustained custom-delivery pressure drives engineering burnout, severe attrition, and morale loss; schedule recovery time, check-ins, and a realistic capacity ceiling.",
            confidence="high",
        ),
        Citation(
            title="Hiring and Team Scaling Note",
            source="demo-data/hiring-scaling-note.md",
            snippet="Hiring to cover a capacity gap takes longer than expected and rarely relieves a near-term delay; treat new headcount as a 6-month investment, not an immediate fix.",
            confidence="medium",
        ),
        Citation(
            title="Reference Customer and Proof-Point Note",
            source="demo-data/reference-customer-note.md",
            snippet="Using an enterprise customer as a public reference can meaningfully increase future sales, but only when the deployment is healthy; a strained or churned reference backfires and reduces credibility.",
            confidence="medium",
        ),
        Citation(
            title="Legal and Contractual Boundary Brief",
            source="demo-data/legal-boundary-brief.md",
            snippet="High-stakes legal and contractual boundaries (liability, IP ownership of custom features, termination terms) deserve explicit guardrails and review before signing.",
            confidence="high",
        ),
        Citation(
            title="Honesty and Disclosure in Relationships",
            source="demo-data/relationship-honesty-brief.md",
            snippet="Transparent, honest communication is necessary for long-term peace and emotional clarity, but partners do not always react to honesty in predictable ways; disclosure of a hidden relationship often causes acute pain before it enables repair, and outcomes depend on timing, delivery, and prior trust.",
            confidence="high",
        ),
        Citation(
            title="Minimizing Harm When Ending a Relationship",
            source="demo-data/minimizing-harm-brief.md",
            snippet="When a choice will hurt a partner, harm is reduced by honesty, taking responsibility, avoiding prolonged uncertainty, and clear boundaries; delaying a decision tends to deepen resentment and emotional distress for everyone involved.",
            confidence="high",
        ),
        Citation(
            title="Trust Repair and Betrayal Note",
            source="demo-data/trust-repair-note.md",
            snippet="Damaged trust can sometimes be rebuilt, but permanent loss of trust is common after concealment; rebuilding requires consistent transparency over time and is not guaranteed, so a partner may end the relationship regardless of intentions.",
            confidence="high",
        ),
        Citation(
            title="Decision Under Emotional Uncertainty",
            source="demo-data/emotional-decision-brief.md",
            snippet="Decisions made under strong emotion and fear of loss, guilt, or being alone are prone to avoidance and indecision; prolonged uncertainty causes both partners frustration and can lead to hidden resentment and breakdown of communication.",
            confidence="high",
        ),
        Citation(
            title="Emotional Wellbeing and Support Note",
            source="demo-data/emotional-wellbeing-note.md",
            snippet="Severe emotional distress, isolation, and depression are real risks during relationship upheaval; protect wellbeing with a support system, professional help if needed, and recovery time rather than facing the fallout alone.",
            confidence="high",
        ),
        Citation(
            title="Social Fallout and Shared Networks Note",
            source="demo-data/social-fallout-note.md",
            snippet="Ending or changing a relationship often produces social fallout affecting shared friend groups and family; mutual connections may take sides, so anticipate changes to your social network and plan support accordingly.",
            confidence="medium",
        ),
        Citation(
            title="Taking Responsibility and Reset Note",
            source="demo-data/responsibility-reset-note.md",
            snippet="Ending both relationships to take responsibility and reset is a legitimate path that prioritizes integrity over comfort; it trades short-term loss and being alone for reduced long-term guilt and a cleaner foundation for future relationships.",
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
        endpoint = (self.settings.foundry_iq_endpoint or "").rstrip("/")
        index_name = self.settings.foundry_iq_index_name
        payload = {
            "search": query.query,
            "top": query.top_k,
            "select": "title,source,content,decision_type",
        }
        headers = {"api-key": self.settings.foundry_iq_api_key or ""}
        try:
            response = httpx.post(
                f"{endpoint}/indexes/{index_name}/docs/search?api-version=2024-07-01",
                json=payload,
                headers=headers,
                timeout=8,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            return MockKnowledgeProvider().retrieve(query)
        data = response.json()
        citations: list[Citation] = []
        for item in data.get("value", [])[: query.top_k]:
            content = item.get("content", "")
            snippet = content[:260] + ("..." if len(content) > 260 else "")
            citations.append(
                Citation(
                    title=item.get("title", "Foundry IQ result"),
                    source=item.get("source", "Foundry IQ"),
                    snippet=snippet,
                    confidence=item.get("confidence", "medium"),
                )
            )
        return citations or MockKnowledgeProvider().retrieve(query)


def get_knowledge_provider(settings: Settings) -> KnowledgeProvider:
    if settings.foundry_iq_configured:
        return FoundryIQKnowledgeProvider(settings)
    return MockKnowledgeProvider()
