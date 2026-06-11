"use client";

import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  Download,
  FileUp,
  FlaskConical,
  Network,
  Radar,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import Image from "next/image";
import { useMemo, useState } from "react";
import { AgentTraceGraph } from "@/components/AgentTraceGraph";
import { ImpactStack, OptionalityQuadrant, RadarChart, RiskHeatmap } from "@/components/DecisionCharts";
import { ScenarioLattice } from "@/components/ScenarioLattice";
import { ScoreBar } from "@/components/ScoreBar";
import { createAndAnalyzeDecision, fetchDemoPackage, samplePrompt } from "@/lib/api";
import { useDecisionStore } from "@/lib/useDecisionStore";
import type { AnalysisPackage, ScenarioSpec } from "@/lib/types";

const horizonSteps = [
  ["H", "Hear the decision context"],
  ["O", "Organize goals and constraints"],
  ["R", "Render plausible futures"],
  ["I", "Identify ripple effects"],
  ["Z", "Zoom into black swans"],
  ["O", "Optimize reversibility"],
  ["N", "Next-step experiments"],
  ["X", "Explain evidence and uncertainty"]
];

const nav = [
  ["comparison", "Scenarios"],
  ["ripple", "Ripple"],
  ["experiment", "Experiment"],
  ["memo", "Memo"]
] as const;

const credibilityItems = [
  { label: "Scenario lattice", icon: Network },
  { label: "Grounded evidence", icon: Radar },
  { label: "Safe experiments", icon: FlaskConical },
  { label: "Safety verifier", icon: ShieldCheck }
];

export function HxrizxnApp() {
  const { screen, setScreen, packageData, setPackageData } = useDecisionStore();
  const [prompt, setPrompt] = useState(samplePrompt);
  const [error, setError] = useState<string | null>(null);
  const [loadingLabel, setLoadingLabel] = useState("Decision Framing Agent");

  async function runDemo() {
    setError(null);
    setScreen("loading");
    const labels = [
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
    ];
    labels.forEach((label, index) => {
      window.setTimeout(() => setLoadingLabel(label), 200 * index);
    });
    try {
      const data = await fetchDemoPackage();
      setPackageData(data);
      setScreen("comparison");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
      setScreen("intake");
    }
  }

  async function runCustom() {
    setError(null);
    setScreen("loading");
    try {
      const data = await createAndAnalyzeDecision(prompt);
      setPackageData(data);
      setScreen("comparison");
    } catch {
      const data = await fetchDemoPackage();
      setPackageData(data);
      setError("API unavailable, showing deterministic demo mode.");
      setScreen("comparison");
    }
  }

  return (
    <main className={`app-shell ${screen === "landing" ? "app-shell--landing" : ""}`}>
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5">
        <button className="focus-ring flex items-center gap-3" onClick={() => setScreen("landing")}>
          <Image src="/logo.png" alt="Hxrizxn AI logo" width={44} height={38} className="h-[38px] w-[44px] rounded object-contain" />
          <span className="text-lg font-semibold">Hxrizxn AI</span>
        </button>
        <div className="hidden items-center gap-2 md:flex">
          {packageData &&
            nav.map(([target, label]) => (
              <button
                key={target}
                className={`focus-ring rounded px-3 py-2 text-sm ${screen === target ? "bg-white text-slate-950" : "text-slate-300 hover:bg-white/10"}`}
                onClick={() => setScreen(target)}
              >
                {label}
              </button>
            ))}
        </div>
      </header>

      {screen === "landing" && <Landing runDemo={runDemo} openIntake={() => setScreen("intake")} />}
      {screen === "intake" && (
        <Intake prompt={prompt} setPrompt={setPrompt} runCustom={runCustom} runDemo={runDemo} error={error} />
      )}
      {screen === "loading" && <Loading label={loadingLabel} />}
      {packageData && screen === "comparison" && <Comparison data={packageData} setScreen={setScreen} />}
      {packageData && screen === "ripple" && <Ripple data={packageData} setScreen={setScreen} />}
      {packageData && screen === "experiment" && <Experiment data={packageData} setScreen={setScreen} />}
      {packageData && screen === "memo" && <Memo data={packageData} setScreen={setScreen} />}
    </main>
  );
}

function Landing({ runDemo, openIntake }: { runDemo: () => void; openIntake: () => void }) {
  return (
    <section className="mx-auto max-w-7xl px-5 pb-20 pt-14">
      <div className="grid min-h-[590px] items-end gap-10 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="pb-10">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/30 px-3 py-2 text-sm text-slate-200">
            <Sparkles size={16} />
            Microsoft Foundry IQ-ready multi-agent reasoning
          </div>
          <h1 className="max-w-3xl text-5xl font-semibold leading-tight md:text-7xl">
            Hxrizxn AI
          </h1>
          <p className="mt-5 max-w-2xl text-xl leading-8 text-slate-200">
            See beyond the obvious future with HORIZON-X, a decision simulator that maps scenarios, ripple effects,
            reversibility, regret, and safer experiments before commitment.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button
              onClick={runDemo}
              className="focus-ring inline-flex items-center gap-2 rounded bg-white px-5 py-3 font-semibold text-slate-950"
            >
              Try Sample Decision <ArrowRight size={18} />
            </button>
            <button
              onClick={openIntake}
              className="focus-ring inline-flex items-center gap-2 rounded border border-white/20 bg-black/30 px-5 py-3 font-semibold text-white"
            >
              Open Intake <BrainCircuit size={18} />
            </button>
          </div>
        </div>
        <div className="panel mb-8 rounded-lg p-4">
          <div className="grid grid-cols-2 gap-3">
            {credibilityItems.map(({ label, icon: Icon }) => (
              <div key={label} className="rounded border border-white/10 bg-white/[0.04] p-4">
                <Icon className="mb-5 text-teal-200" size={24} />
                <div className="text-sm font-semibold text-white">{label}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded border border-white/10 bg-black/25 p-4 text-sm text-slate-300">
            Hxrizxn AI is decision support, not a licensed professional.
          </div>
        </div>
      </div>

      <div className="grid gap-3 md:grid-cols-4">
        {horizonSteps.map(([letter, text]) => (
          <div key={`${letter}-${text}`} className="panel rounded-lg p-4">
            <div className="text-2xl font-semibold text-teal-200">{letter}</div>
            <div className="mt-2 text-sm text-slate-200">{text}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function Intake({
  prompt,
  setPrompt,
  runCustom,
  runDemo,
  error
}: {
  prompt: string;
  setPrompt: (value: string) => void;
  runCustom: () => void;
  runDemo: () => void;
  error: string | null;
}) {
  return (
    <section className="mx-auto grid max-w-7xl gap-6 px-5 pb-20 pt-10 lg:grid-cols-[1fr_0.7fr]">
      <div className="panel rounded-lg p-5">
        <div className="mb-4 flex items-center gap-2 text-sm text-teal-200">
          <BrainCircuit size={18} />
          Decision Intake
        </div>
        <textarea
          className="focus-ring min-h-[260px] w-full resize-y rounded border border-white/15 bg-black/30 p-4 text-base leading-7 text-white"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
        />
        <div className="mt-4 grid gap-3 md:grid-cols-2">
          {["Goals: autonomy, learning", "Fears: burn rate, isolation", "Money limit: 8 months", "Timeline: 18 months"].map(
            (item) => (
              <div key={item} className="rounded border border-white/10 bg-white/[0.04] px-3 py-3 text-sm text-slate-200">
                {item}
              </div>
            )
          )}
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button onClick={runCustom} className="focus-ring inline-flex items-center gap-2 rounded bg-white px-5 py-3 font-semibold text-slate-950">
            Analyze Decision <ArrowRight size={18} />
          </button>
          <button onClick={runDemo} className="focus-ring rounded border border-white/20 px-5 py-3 font-semibold text-white">
            Try Sample Decision
          </button>
          <label className="focus-ring inline-flex items-center gap-2 rounded border border-white/20 px-4 py-3 text-sm text-slate-200">
            <FileUp size={18} />
            Upload Docs
            <input type="file" className="sr-only" multiple />
          </label>
        </div>
        {error && <div className="mt-4 rounded border border-amber-300/40 bg-amber-300/10 p-3 text-sm text-amber-100">{error}</div>}
      </div>
      <div className="panel rounded-lg p-5">
        <h2 className="text-xl font-semibold">Sample Decisions</h2>
        <div className="mt-4 space-y-3">
          {[
            "Should I quit my job and start a startup?",
            "Should I move to another country?",
            "Should I pursue graduate school?",
            "Should I buy a house?",
            "Should I switch careers?"
          ].map((item) => (
            <button
              key={item}
              className="focus-ring flex w-full items-center justify-between rounded border border-white/10 bg-white/[0.04] p-3 text-left text-sm text-slate-200 hover:bg-white/10"
              onClick={() => setPrompt(item)}
            >
              {item}
              <ArrowRight size={16} />
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}

function Loading({ label }: { label: string }) {
  const agents = [
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
  ];
  return (
    <section className="mx-auto max-w-7xl px-5 pb-20 pt-12">
      <div className="panel rounded-lg p-6">
        <div className="flex items-center gap-3 text-teal-200">
          <Activity className="animate-pulse" />
          <span>{label}</span>
        </div>
        <h2 className="mt-4 text-3xl font-semibold">HORIZON-X analysis running</h2>
        <div className="mt-6 grid gap-3 md:grid-cols-3">
          {agents.map((agent, index) => (
            <motion.div
              key={agent}
              initial={{ opacity: 0.4, y: 8 }}
              animate={{ opacity: label === agent ? 1 : 0.72, y: 0 }}
              transition={{ delay: index * 0.03 }}
              className={`rounded border p-4 ${label === agent ? "border-teal-200 bg-teal-200/10" : "border-white/10 bg-white/[0.04]"}`}
            >
              <div className="text-sm font-semibold">{agent}</div>
              <div className="mt-2 text-xs text-slate-300">Structured JSON output, trace visible, chain-of-thought hidden.</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Comparison({ data, setScreen }: { data: AnalysisPackage; setScreen: (screen: "ripple") => void }) {
  return (
    <section className="mx-auto max-w-7xl px-5 pb-20 pt-8">
      <SectionHeader icon={Network} eyebrow="Scenario Comparison" title={data.framed_decision.title} />
      <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="panel rounded-lg p-4">
          <ScenarioLattice scenarios={data.scenarios} />
        </div>
        <div className="panel rounded-lg p-4">
          <RadarChart data={data} />
        </div>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        {data.scenarios.map((scenario) => (
          <ScenarioCard key={scenario.scenario_key} scenario={scenario} />
        ))}
      </div>
      <NextButton onClick={() => setScreen("ripple")} label="Open Ripple Effects" />
    </section>
  );
}

function ScenarioCard({ scenario }: { scenario: ScenarioSpec }) {
  return (
    <article className="panel rounded-lg p-5">
      <div className="text-sm uppercase tracking-wide text-slate-400">{scenario.probability_band}</div>
      <h3 className="mt-2 text-xl font-semibold">{scenario.scenario_name}</h3>
      <p className="mt-3 min-h-[112px] text-sm leading-6 text-slate-300">{scenario.narrative}</p>
      <div className="mt-5 space-y-3">
        <ScoreBar label="Upside" value={scenario.upside_score} tone="teal" />
        <ScoreBar label="Downside" value={scenario.downside_score} tone="rose" />
        <ScoreBar label="Regret" value={scenario.regret_score} tone="amber" />
        <ScoreBar label="Reversibility" value={scenario.reversibility_score} tone="violet" />
        <ScoreBar label="Optionality" value={scenario.optionality_score} tone="teal" />
      </div>
    </article>
  );
}

function Ripple({ data, setScreen }: { data: AnalysisPackage; setScreen: (screen: "experiment") => void }) {
  return (
    <section className="mx-auto max-w-7xl px-5 pb-20 pt-8">
      <SectionHeader icon={AlertTriangle} eyebrow="Ripple Effects" title="Second-order consequences and risk map" />
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="panel rounded-lg p-4">
          <RiskHeatmap data={data} />
        </div>
        <div className="panel rounded-lg p-4">
          <ImpactStack data={data} />
        </div>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="panel rounded-lg p-4">
          <OptionalityQuadrant data={data} />
        </div>
        <div className="panel rounded-lg p-4">
          <AgentTraceGraph trace={data.trace} />
        </div>
      </div>
      <NextButton onClick={() => setScreen("experiment")} label="Open Experiment Plan" />
    </section>
  );
}

function Experiment({ data, setScreen }: { data: AnalysisPackage; setScreen: (screen: "memo") => void }) {
  const plan = data.experiment_plan;
  return (
    <section className="mx-auto max-w-7xl px-5 pb-20 pt-8">
      <SectionHeader icon={FlaskConical} eyebrow="Experiment Plan" title={plan.plan_name} />
      <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="panel rounded-lg p-5">
          <div className="flex items-center gap-2 text-teal-200">
            <CheckCircle2 size={20} />
            {plan.duration_days} days - reversible
          </div>
          <p className="mt-4 text-lg leading-8 text-slate-200">{plan.hypothesis}</p>
          <ListBlock title="Steps" items={plan.steps} />
        </div>
        <div className="grid gap-5">
          <div className="panel rounded-lg p-5">
            <ListBlock title="Success Criteria" items={plan.success_criteria} />
          </div>
          <div className="panel rounded-lg p-5">
            <ListBlock title="Stop Conditions" items={plan.stop_conditions} tone="rose" />
          </div>
          <div className="panel rounded-lg p-5">
            <ListBlock title="What You Will Learn" items={plan.what_you_will_learn} tone="amber" />
          </div>
        </div>
      </div>
      <NextButton onClick={() => setScreen("memo")} label="Open Decision Memo" />
    </section>
  );
}

function Memo({ data }: { data: AnalysisPackage; setScreen: (screen: "comparison") => void }) {
  const reportUrl = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/cases/${data.case_id}/report`;
  const citations = useMemo(() => data.memo.citations.slice(0, 4), [data.memo.citations]);
  return (
    <section className="mx-auto max-w-5xl px-5 pb-20 pt-8">
      <SectionHeader icon={ShieldCheck} eyebrow="Decision Memo" title="Proceed via reversible experiment" />
      <article className="panel rounded-lg p-6">
        <h2 className="text-2xl font-semibold">{data.memo.recommendation_summary}</h2>
        <p className="mt-5 text-lg leading-8 text-slate-200">{data.memo.rationale}</p>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded border border-white/10 bg-white/[0.04] p-4">
            <div className="text-sm text-slate-400">Still Unknown</div>
            <p className="mt-2 text-slate-200">{data.memo.uncertainty_notes}</p>
          </div>
          <div className="rounded border border-white/10 bg-white/[0.04] p-4">
            <div className="text-sm text-slate-400">Safer Next Move</div>
            <p className="mt-2 text-slate-200">{data.memo.safer_next_move}</p>
          </div>
        </div>
        <div className="mt-6 rounded border border-teal-200/30 bg-teal-200/10 p-4 text-sm text-teal-50">
          {data.memo.disclaimers}
        </div>
        {citations.length > 0 && (
          <div className="mt-6">
            <h3 className="font-semibold">Grounded Evidence</h3>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              {citations.map((citation) => (
                <div key={`${citation.title}-${citation.source}`} className="rounded border border-white/10 bg-white/[0.04] p-3">
                  <div className="text-sm font-semibold">{citation.title}</div>
                  <div className="mt-1 text-xs text-slate-400">{citation.source}</div>
                  <p className="mt-2 text-sm text-slate-300">{citation.snippet}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        <a
          className="focus-ring mt-6 inline-flex items-center gap-2 rounded bg-white px-5 py-3 font-semibold text-slate-950"
          href={reportUrl}
          target="_blank"
          rel="noreferrer"
        >
          Export Report <Download size={18} />
        </a>
      </article>
    </section>
  );
}

function SectionHeader({
  icon: Icon,
  eyebrow,
  title
}: {
  icon: typeof Network;
  eyebrow: string;
  title: string;
}) {
  return (
    <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
      <div>
        <div className="flex items-center gap-2 text-sm text-teal-200">
          <Icon size={18} />
          {eyebrow}
        </div>
        <h1 className="mt-2 text-3xl font-semibold md:text-4xl">{title}</h1>
      </div>
      <div className="rounded border border-white/15 bg-black/30 px-3 py-2 text-sm text-slate-300">
        Hxrizxn AI is decision support, not a licensed professional.
      </div>
    </div>
  );
}

function ListBlock({ title, items, tone = "teal" }: { title: string; items: string[]; tone?: "teal" | "amber" | "rose" }) {
  const color = tone === "rose" ? "text-rose-200" : tone === "amber" ? "text-amber-200" : "text-teal-200";
  return (
    <div className="mt-5">
      <h3 className={`font-semibold ${color}`}>{title}</h3>
      <ul className="mt-3 space-y-3">
        {items.map((item) => (
          <li key={item} className="flex gap-3 text-sm leading-6 text-slate-200">
            <CheckCircle2 className={color} size={18} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function NextButton({ onClick, label }: { onClick: () => void; label: string }) {
  return (
    <div className="mt-6 flex justify-end">
      <button onClick={onClick} className="focus-ring inline-flex items-center gap-2 rounded bg-white px-5 py-3 font-semibold text-slate-950">
        {label} <ArrowRight size={18} />
      </button>
    </div>
  );
}
