export type Band = "low" | "medium" | "high" | "very_high";

export type Citation = {
  title: string;
  source: string;
  snippet: string;
  confidence: Band;
};

export type DecisionOption = {
  option_key: string;
  label: string;
  description: string;
};

export type SafetyFlag = {
  domain: string;
  severity: "info" | "caution" | "escalate" | "block";
  message: string;
  recommended_boundary: string;
};

export type GroundedClaim = {
  text: string;
  status: "grounded" | "unverified";
  source: string | null;
  source_title: string | null;
};

export type FramedDecision = {
  case_id: string;
  title: string;
  decision_type: string;
  goals: string[];
  fears: string[];
  constraints: string[];
  assumptions: string[];
  grounded_assumptions: GroundedClaim[];
  missing_information: string[];
  candidate_options: DecisionOption[];
  high_stakes_flags: SafetyFlag[];
  evidence: Citation[];
};

export type ScenarioSpec = {
  scenario_key: "optimistic" | "base" | "stress";
  scenario_name: string;
  narrative: string;
  branching_logic: string[];
  confidence_label: string;
  probability_band: string;
  time_horizon: string;
  upside_score: number;
  downside_score: number;
  regret_score: number;
  reversibility_score: number;
  optionality_score: number;
  evidence: Citation[];
};

export type ScenarioImpact = {
  scenario_key: string;
  domain: string;
  order_level: 1 | 2 | 3;
  impact_direction: "positive" | "negative" | "mixed" | "neutral";
  severity: number;
  explanation: string;
};

export type RiskItem = {
  scenario_key: string;
  risk_name: string;
  risk_type: string;
  likelihood_band: Band;
  severity_band: Band;
  detectability_band: Band;
  mitigation: string;
  black_swan: boolean;
  grounding_status: "grounded" | "unverified";
  grounding_source: string | null;
};

export type ExperimentPlan = {
  plan_name: string;
  hypothesis: string;
  duration_days: number;
  reversible: boolean;
  steps: string[];
  success_criteria: string[];
  stop_conditions: string[];
  what_you_will_learn: string[];
};

export type DecisionMemo = {
  recommendation_summary: string;
  rationale: string;
  uncertainty_notes: string;
  safer_next_move: string;
  disclaimers: string;
  citations: Citation[];
};

export type AgentTraceView = {
  agent_name: string;
  status: string;
  input_summary: string;
  output_summary: string;
  started_at: string;
  completed_at: string | null;
  latency_ms: number;
};

export type AnalysisPackage = {
  case_id: string;
  horizon_x_stage: string;
  framed_decision: FramedDecision;
  scenarios: ScenarioSpec[];
  impacts: ScenarioImpact[];
  risks: RiskItem[];
  experiment_plan: ExperimentPlan;
  safety_flags: SafetyFlag[];
  memo: DecisionMemo;
  trace: AgentTraceView[];
};

