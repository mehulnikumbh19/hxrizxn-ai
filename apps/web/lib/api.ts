import type { AnalysisPackage } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const samplePrompt =
  "I'm a software engineer with 3 years of experience. I have savings for 8 months. I want to quit my job and start an AI startup, but I'm worried about burn rate, isolation, and whether I'm romanticizing founder life. Should I quit now, wait 6 months, or test the idea part-time first?";

export async function createAndAnalyzeDecision(raw_prompt: string): Promise<AnalysisPackage> {
  const created = await fetch(`${API_URL}/api/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      title: "Quit job or test the AI startup first?",
      decision_type: "startup",
      raw_prompt,
      goals: ["Founder autonomy", "Learning velocity", "Avoid irreversible regret"],
      fears: ["Burn rate", "Isolation", "Romanticizing founder life"],
      constraints: ["8 months savings", "Current job provides stable income"],
      money_limit_months: 8,
      time_horizon_months: 18
    })
  });
  if (!created.ok) {
    throw new Error("Could not create case");
  }
  const caseData = await created.json();
  const analyzed = await fetch(`${API_URL}/api/cases/${caseData.id}/analyze`, { method: "POST" });
  if (!analyzed.ok) {
    throw new Error("Could not analyze case");
  }
  return analyzed.json();
}

export async function fetchDemoPackage(): Promise<AnalysisPackage> {
  try {
    const response = await fetch(`${API_URL}/api/demo/scenarios`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error("Demo endpoint unavailable");
    }
    return response.json();
  } catch {
    return fallbackPackage;
  }
}

export const fallbackPackage: AnalysisPackage = {
  case_id: "demo-fallback",
  horizon_x_stage: "X - Explain recommendation, uncertainty, and evidence",
  framed_decision: {
    case_id: "demo-fallback",
    title: "Quit job or test the AI startup first?",
    decision_type: "startup",
    goals: ["Founder autonomy", "Learning velocity", "Avoid irreversible regret"],
    fears: ["Burn rate", "Isolation", "Romanticizing founder life"],
    constraints: ["8 months savings", "Stable job income"],
    assumptions: ["The riskiest assumptions can be tested before resignation."],
    missing_information: ["Exact burn floor", "Customer evidence", "Support plan"],
    candidate_options: [
      { option_key: "quit_now", label: "Quit now", description: "Pursue full-time immediately." },
      { option_key: "wait_six_months", label: "Wait 6 months", description: "Preserve income and save runway." },
      { option_key: "part_time_test", label: "Test part-time first", description: "Validate before resigning." }
    ],
    high_stakes_flags: [],
    evidence: [
      {
        title: "Startup Burn Rate Note",
        source: "demo-data/startup-idea-note.md",
        snippet: "Founder risk is dominated by runway, customer evidence, isolation, and execution cadence.",
        confidence: "high"
      }
    ]
  },
  scenarios: [
    {
      scenario_key: "optimistic",
      scenario_name: "Controlled Upside Branch",
      narrative: "Urgency becomes disciplined validation, with early customer evidence and protected runway.",
      branching_logic: ["Test assumptions", "Protect support", "Avoid premature irreversible commitments"],
      confidence_label: "Credible upside",
      probability_band: "plausible but evidence-sensitive",
      time_horizon: "6-18 months",
      upside_score: 82,
      downside_score: 38,
      regret_score: 32,
      reversibility_score: 62,
      optionality_score: 74,
      evidence: []
    },
    {
      scenario_key: "base",
      scenario_name: "Evidence-Building Base Case",
      narrative: "A part-time validation sprint preserves income and reveals whether demand is real.",
      branching_logic: ["Run interviews", "Ask for commitment", "Review runway weekly"],
      confidence_label: "Most robust",
      probability_band: "moderately likely",
      time_horizon: "30-90 days",
      upside_score: 76,
      downside_score: 24,
      regret_score: 22,
      reversibility_score: 88,
      optionality_score: 91,
      evidence: []
    },
    {
      scenario_key: "stress",
      scenario_name: "Runway Compression Stress Case",
      narrative: "Weak signals are treated as proof and burn rate compresses options before traction exists.",
      branching_logic: ["Commit too early", "Ignore weak evidence", "Compress fallback options"],
      confidence_label: "Stress test",
      probability_band: "possible under poor guardrails",
      time_horizon: "3-12 months",
      upside_score: 44,
      downside_score: 78,
      regret_score: 68,
      reversibility_score: 34,
      optionality_score: 41,
      evidence: []
    }
  ],
  impacts: [
    { scenario_key: "base", domain: "finances", order_level: 2, impact_direction: "mixed", severity: 4, explanation: "Income preservation keeps later choices available." },
    { scenario_key: "base", domain: "career", order_level: 3, impact_direction: "mixed", severity: 4, explanation: "Portfolio evidence changes future opportunities." },
    { scenario_key: "stress", domain: "health_energy", order_level: 2, impact_direction: "negative", severity: 5, explanation: "Isolation and ambiguity compound decision fatigue." }
  ],
  risks: [
    { scenario_key: "base", risk_name: "Runway compression", risk_type: "execution", likelihood_band: "medium", severity_band: "high", detectability_band: "medium", mitigation: "Define a cash floor and stop condition.", black_swan: false },
    { scenario_key: "stress", risk_name: "External shock during low-liquidity window", risk_type: "black_swan", likelihood_band: "low", severity_band: "very_high", detectability_band: "low", mitigation: "Keep emergency reserve and re-entry plan.", black_swan: true }
  ],
  experiment_plan: {
    plan_name: "30-day reversible HORIZON-X validation sprint",
    hypothesis: "If demand survives a small test, the user can commit later with less regret exposure.",
    duration_days: 30,
    reversible: true,
    steps: ["Interview 15 target users", "Build a concierge prototype", "Ask for 2 concrete commitments", "Review runway weekly"],
    success_criteria: ["5 strong problem confirmations", "2 concrete commitments", "Sustainable weekly energy"],
    stop_conditions: ["Runway falls below safety floor", "Repeated disconfirming evidence", "Isolation becomes acute"],
    what_you_will_learn: ["Whether demand is real", "Whether founder life is energizing", "Whether commitment should increase"]
  },
  safety_flags: [],
  memo: {
    recommendation_summary: "Proceed via experiment: do not make the full irreversible move yet.",
    rationale: "HORIZON-X favors the base branch because it preserves optionality, reduces action regret, and turns the decision into evidence-generating milestones.",
    uncertainty_notes: "The largest unknowns are customer demand, founder energy, and runway tolerance.",
    safer_next_move: "Interview 15 target users and ask for concrete commitments.",
    disclaimers: "Hxrizxn AI is decision support, not a licensed professional.",
    citations: []
  },
  trace: [
    "Decision Framing Agent",
    "Evidence Grounding Agent",
    "Assumption Miner Agent",
    "Scenario Lattice Agent",
    "Ripple Effects Agent",
    "Regret and Reversibility Agent",
    "Black Swan Agent",
    "Future Self Agent",
    "Experiment Design Agent",
    "Safety and Boundary Agent",
    "Recommendation Composer Agent"
  ].map((agent_name, index) => ({
    agent_name,
    status: "completed",
    input_summary: "Structured JSON contract",
    output_summary: "Validated output package",
    started_at: new Date(Date.now() + index * 100).toISOString(),
    completed_at: new Date(Date.now() + index * 140).toISOString(),
    latency_ms: 40 + index * 11
  }))
};

