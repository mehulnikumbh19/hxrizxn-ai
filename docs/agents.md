# Agents

All agents use typed JSON contracts from `apps/api/app/schemas.py` and versioned prompt files in `packages/agent-prompts`.

1. Decision Framing Agent: converts messy input into goals, fears, constraints, assumptions, missing info, and options.
2. Scenario Lattice Agent: renders optimistic, base, and stress futures with scorecards.
3. Ripple Effects Agent: maps first-, second-, and third-order effects across six domains.
4. Risk and Black Swan Agent: builds risk register, mitigations, detectability, and black-swan flags.
5. Optionality and Reversibility Agent: scores lock-in, undo cost, and option preservation.
6. Regret and Future Self Agent: models missed-opportunity regret, action regret, and identity alignment.
7. Experiment Design Agent: creates a reversible 30-day validation sprint.
8. Verifier and Safety Agent: checks coverage, consistency, high-stakes domains, and disclaimer needs.
9. Recommendation Composer Agent: produces the final memo and citations.

The UI trace panel shows these roles as observable workflow nodes without revealing chain-of-thought.

