export type ScenarioKey = "optimistic" | "base" | "stress";

export type Scorecard = {
  upside_score: number;
  downside_score: number;
  regret_score: number;
  reversibility_score: number;
  optionality_score: number;
};

export type AgentRole =
  | "Decision Framing Agent"
  | "Scenario Lattice Agent"
  | "Ripple Effects Agent"
  | "Risk and Black Swan Agent"
  | "Optionality and Reversibility Agent"
  | "Regret and Future Self Agent"
  | "Experiment Design Agent"
  | "Verifier and Safety Agent"
  | "Recommendation Composer Agent";

