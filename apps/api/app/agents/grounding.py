from __future__ import annotations

from app.providers.knowledge import KnowledgeProvider, RetrievalQuery
from app.schemas import Citation, FramedDecision


def retrieve_evidence(framed: FramedDecision, knowledge: KnowledgeProvider) -> list[Citation]:
    """Retrieve grounding evidence based on the decision brief and domain tags."""
    query_str = f"{framed.title} {framed.decision_type} optionality regret second-order consequences"
    query = RetrievalQuery(
        case_id=framed.case_id,
        query=query_str,
        decision_type=framed.decision_type,
        top_k=4,
    )
    return knowledge.retrieve(query)
