from __future__ import annotations

from app.schemas import FramedDecision, ScenarioSpec


def generate_future_self_postcards(framed: FramedDecision, scenarios: list[ScenarioSpec]) -> dict[str, str]:
    """Generate 'future self' reflections per scenario branch."""
    postcards = {}
    for scenario in scenarios:
        key = scenario.scenario_key
        if key == "base":
            postcard = (
                "A year from now, future you is relieved that curiosity was honored without forcing a brittle leap."
            )
        elif key == "optimistic":
            postcard = (
                "Future you is proud of the courage, but remembers that the courage worked because guardrails existed."
            )
        else:
            postcard = (
                "Future you wishes the first move had been smaller, because the lesson was available before the full cost."
            )

        if framed.decision_type == "startup":
            if key == "base":
                postcard = (
                    "A year from now, you are glad you ran a 30-day pilot before resigning. "
                    "The customer evidence you gathered saved you from quitting blindly."
                )
        elif framed.decision_type == "relocation":
            if key == "base":
                postcard = (
                    "A year from now, you appreciate that you tested the new country with a trial stay. "
                    "It helped you build a local network before committing to a one-way move."
                )

        postcards[key] = postcard
    return postcards
