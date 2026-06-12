"use client";

import { motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  Briefcase,
  CheckCircle2,
  Clock,
  Download,
  FileUp,
  FlaskConical,
  GraduationCap,
  HelpCircle,
  Home,
  Lightbulb,
  Network,
  Plane,
  Radar,
  Rocket,
  ShieldCheck,
  Sparkles,
  Target,
  Wallet,
  Waves,
  XCircle
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
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

const stepGradients = [
  "linear-gradient(135deg, #0f6cbd, #479ef5)",
  "linear-gradient(135deg, #5b5fc7, #7f85f5)",
  "linear-gradient(135deg, #c238b3, #e07bd2)",
  "linear-gradient(135deg, #107c10, #54b054)"
];

const nav = [
  ["comparison", "Scenarios"],
  ["ripple", "Ripple"],
  ["experiment", "Experiment"],
  ["memo", "Memo"]
] as const;

const credibilityItems = [
  { label: "Scenario lattice", icon: Network, fg: "#0f6cbd", bg: "#ebf3fc" },
  { label: "Grounded evidence", icon: Radar, fg: "#5b5fc7", bg: "#eeeffb" },
  { label: "Safe experiments", icon: FlaskConical, fg: "#107c10", bg: "#f1faf1" },
  { label: "Safety verifier", icon: ShieldCheck, fg: "#c238b3", bg: "#fbeffa" }
];

const agentLabels = [
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

const agentBlurbs = [
  "Turning your messy real-world situation into one precise, answerable question.",
  "Pulling in grounded evidence so the analysis is anchored in reality, not vibes.",
  "Digging out the hidden assumptions your decision quietly depends on.",
  "Branching your future into optimistic, base and stress scenarios.",
  "Tracing how this choice ripples across money, career, relationships and health.",
  "Asking the hard question: if this goes wrong, how easily can you undo it?",
  "Stress-testing the plan against rare but devastating surprises.",
  "Consulting the you of five years from now about regret and pride.",
  "Designing a small, cheap, reversible experiment to run before you leap.",
  "Checking guardrails: budget limits, time limits and personal boundaries.",
  "Composing the final memo: recommendation, evidence and honest uncertainty."
];

function BrandMark({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="hx-grad" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="#0f6cbd" />
          <stop offset="0.5" stopColor="#5b5fc7" />
          <stop offset="1" stopColor="#c238b3" />
        </linearGradient>
      </defs>
      <rect x="1" y="1" width="30" height="30" rx="9" fill="url(#hx-grad)" opacity="0.13" />
      <path d="M10 10 L22 22 M22 10 L10 22" stroke="url(#hx-grad)" strokeWidth="3.4" strokeLinecap="round" />
    </svg>
  );
}

export function HxrizxnApp() {
  const { screen, setScreen, packageData, setPackageData } = useDecisionStore();
  const [prompt, setPrompt] = useState(samplePrompt);
  const [error, setError] = useState<string | null>(null);
  const [isFallbackDemo, setIsFallbackDemo] = useState(false);
  const [loadingLabel, setLoadingLabel] = useState("Decision Framing Agent");
  const [loadingStartedAt, setLoadingStartedAt] = useState<number | null>(null);
  const [loadingElapsedSec, setLoadingElapsedSec] = useState(0);
  const loadingTimers = useRef<number[]>([]);

  const [goals, setGoals] = useState("autonomy, learning");
  const [fears, setFears] = useState("burn rate, isolation");
  const [moneyLimit, setMoneyLimit] = useState<number>(8);
  const [timeHorizon, setTimeHorizon] = useState<number>(18);

  // Rehydrate the persisted store on the client only (store uses skipHydration
  // to avoid an SSR hydration mismatch).
  useEffect(() => {
    void useDecisionStore.persist.rehydrate();
  }, []);

  useEffect(() => {
    if (screen !== "loading" || loadingStartedAt === null) {
      return;
    }
    const intervalId = window.setInterval(() => {
      setLoadingElapsedSec(Math.floor((Date.now() - loadingStartedAt) / 1000));
    }, 1000);
    return () => window.clearInterval(intervalId);
  }, [loadingStartedAt, screen]);

  function clearLoadingTimers() {
    loadingTimers.current.forEach((timer) => window.clearTimeout(timer));
    loadingTimers.current = [];
  }

  function startLoadingSequence() {
    clearLoadingTimers();
    setLoadingStartedAt(Date.now());
    setLoadingElapsedSec(0);
    setLoadingLabel(agentLabels[0]);
    const intervalMs = 10_000;
    agentLabels.forEach((label, index) => {
      const timer = window.setTimeout(() => setLoadingLabel(label), intervalMs * index);
      loadingTimers.current.push(timer);
    });
  }

  async function runDemo() {
    setError(null);
    setIsFallbackDemo(false);
    setScreen("loading");
    startLoadingSequence();
    try {
      const data = await fetchDemoPackage();
      clearLoadingTimers();
      setPackageData(data);
      setScreen("comparison");
    } catch (err) {
      clearLoadingTimers();
      setError(err instanceof Error ? err.message : "Analysis failed");
      setScreen("intake");
    }
  }

  async function runCustom() {
    const trimmedPrompt = prompt.trim();
    if (!trimmedPrompt) {
      setError("Describe the decision you want to analyze before running.");
      setScreen("intake");
      return;
    }
    if (!Number.isFinite(moneyLimit) || moneyLimit <= 0) {
      setError("Money limit (months) must be a number greater than 0.");
      setScreen("intake");
      return;
    }
    if (!Number.isFinite(timeHorizon) || timeHorizon <= 0) {
      setError("Time horizon (months) must be a number greater than 0.");
      setScreen("intake");
      return;
    }
    setError(null);
    setIsFallbackDemo(false);
    setScreen("loading");
    startLoadingSequence();
    try {
      const goalsList = goals.split(",").map(g => g.trim()).filter(Boolean);
      const fearsList = fears.split(",").map(f => f.trim()).filter(Boolean);
      const data = await createAndAnalyzeDecision(trimmedPrompt, goalsList, fearsList, moneyLimit, timeHorizon);
      clearLoadingTimers();
      setPackageData(data);
      setScreen("comparison");
    } catch (err) {
      const data = await fetchDemoPackage();
      clearLoadingTimers();
      setPackageData(data);
      setIsFallbackDemo(true);
      setError("API unavailable, showing deterministic demo mode. Details: " + (err instanceof Error ? err.message : String(err)));
      setScreen("comparison");
    }
  }

  return (
    <main className={`app-shell ${screen === "landing" ? "app-shell--landing" : ""}`}>
      {/* Fluent command bar, frosted, with a segmented pill nav */}
      <header className="sticky top-0 z-50 border-b border-[var(--colorNeutralStrokeSubtle)] bg-[rgba(247,246,244,0.78)] backdrop-blur-xl">
        <div className="mx-auto flex h-[60px] max-w-[1240px] items-center justify-between px-6">
          <button className="focus-ring flex items-center gap-2.5 rounded-xl" onClick={() => setScreen("landing")}>
            <BrandMark />
            <span className="text-[15px] font-semibold tracking-tight">Hxrizxn<span className="text-[var(--colorNeutralForeground4)]"> AI</span></span>
          </button>

          {packageData ? (
            <nav className="hidden items-center rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/70 p-1 shadow-[var(--shadow2)] backdrop-blur md:flex">
              {nav.map(([target, label]) => (
                <button
                  key={target}
                  className={`focus-ring relative rounded-full px-4 py-1.5 text-[13px] font-medium transition-colors ${
                    screen === target
                      ? "text-white"
                      : "text-[var(--colorNeutralForeground3)] hover:text-[var(--colorNeutralForeground1)]"
                  }`}
                  onClick={() => setScreen(target)}
                >
                  {screen === target && (
                    <motion.span
                      layoutId="nav-pill"
                      className="absolute inset-0 -z-10 rounded-full bg-gradient-brand shadow-[0_2px_8px_rgba(35,70,170,0.28)]"
                      transition={{ type: "spring", stiffness: 420, damping: 34 }}
                    />
                  )}
                  {label}
                </button>
              ))}
            </nav>
          ) : (
            <span className="hidden items-center gap-2 rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/60 px-3.5 py-1.5 text-[12px] font-medium text-[var(--colorNeutralForeground3)] md:inline-flex">
              <ShieldCheck size={13} className="text-[var(--colorBrandForeground1)]" />
              Decision intelligence
            </span>
          )}
        </div>
      </header>

      {isFallbackDemo && ["comparison", "ripple", "experiment", "memo"].includes(screen) && (
        <div className="mx-auto max-w-7xl px-6 pt-6">
          <div className="flex items-start gap-3 rounded-xl border border-[rgba(188,91,9,0.25)] bg-[var(--colorStatusWarningBackground)] p-3.5 text-sm text-[var(--colorStatusWarningForeground)]">
            <AlertTriangle size={17} className="mt-0.5 shrink-0" />
            <span>
              Live analysis was unavailable, so this is unrelated demo content shown as a fallback. It does not reflect
              your prompt. Try again in a moment, or check your connection to the API.
            </span>
          </div>
        </div>
      )}

      {screen === "landing" && (
        <Landing
          runDemo={runDemo}
          openIntake={() => setScreen("intake")}
          startWith={(p) => {
            setPrompt(p);
            setScreen("intake");
          }}
        />
      )}
      {screen === "intake" && (
        <Intake
          prompt={prompt}
          setPrompt={setPrompt}
          goals={goals}
          setGoals={setGoals}
          fears={fears}
          setFears={setFears}
          moneyLimit={moneyLimit}
          setMoneyLimit={setMoneyLimit}
          timeHorizon={timeHorizon}
          setTimeHorizon={setTimeHorizon}
          runCustom={runCustom}
          runDemo={runDemo}
          error={error}
        />
      )}
      {screen === "loading" && <Loading label={loadingLabel} elapsedSec={loadingElapsedSec} />}
      {packageData && screen === "comparison" && (
        <Comparison data={packageData} setScreen={setScreen} />
      )}
      {packageData && screen === "ripple" && <Ripple data={packageData} setScreen={setScreen} />}
      {packageData && screen === "experiment" && <Experiment data={packageData} setScreen={setScreen} />}
      {packageData && screen === "memo" && <Memo data={packageData} setScreen={setScreen} />}
    </main>
  );
}

/* ================================================================
   LANDING
   ================================================================ */

const landingQuickPicks = [
  "Should I quit my job to start a startup?",
  "Should I move abroad for a new role?",
  "Should I go back to grad school?",
  "Should I buy a house now or keep renting?"
];

function Landing({
  runDemo,
  openIntake,
  startWith
}: {
  runDemo: () => void;
  openIntake: () => void;
  startWith: (prompt: string) => void;
}) {
  const [draft, setDraft] = useState("");

  function submit() {
    const text = draft.trim();
    if (text) {
      startWith(text);
    } else {
      openIntake();
    }
  }

  return (
    <section className="relative mx-auto max-w-[1240px] px-6 pb-28 pt-16 md:pt-24">
      {/* Ambient glow behind the hero (landing only) */}
      <div aria-hidden className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[560px] overflow-hidden">
        <div className="glow left-1/2 top-[-120px] h-[420px] w-[680px] -translate-x-1/2" style={{ background: "radial-gradient(circle, rgba(75,84,200,0.22), transparent 65%)" }} />
        <div className="glow left-[18%] top-[40px] h-[300px] w-[360px]" style={{ background: "radial-gradient(circle, rgba(15,108,189,0.16), transparent 65%)" }} />
      </div>

      {/* Centered, elegant intro */}
      <div className="mx-auto max-w-3xl text-center">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0, 0, 0, 1] }}
          className="inline-flex items-center gap-2 rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/70 px-3.5 py-1.5 text-[12px] font-medium text-[var(--colorNeutralForeground3)] shadow-[var(--shadow2)] backdrop-blur-xl"
        >
          <Sparkles size={13} className="text-[var(--colorAccentIndigo)]" />
          Multi-agent decision intelligence
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.06, ease: [0, 0, 0, 1] }}
          className="mt-6 text-balance text-[40px] font-bold leading-[1.05] tracking-tight text-[var(--colorNeutralForeground1)] md:text-[60px]"
        >
          See beyond the
          <br className="hidden sm:block" /> <span className="text-gradient">obvious future</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, delay: 0.12, ease: [0, 0, 0, 1] }}
          className="mx-auto mt-5 max-w-xl text-[17px] leading-8 text-[var(--colorNeutralForeground3)]"
        >
          HORIZON-X maps scenarios, ripple effects, reversibility, regret and safer
          experiments, so you can pressure-test a life-changing decision before you commit.
        </motion.p>

        {/* Refined prompt box */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.18, ease: [0, 0, 0, 1] }}
          className="mx-auto mt-9 max-w-2xl"
        >
          <div className="panel--glass flex items-center gap-2 rounded-full p-2 pl-5">
            <BrainCircuit size={18} className="shrink-0 text-[var(--colorAccentIndigo)]" />
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submit();
              }}
              placeholder="Describe the decision keeping you up at night..."
              className="focus-ring min-w-0 flex-1 bg-transparent py-2.5 text-[15px] text-[var(--colorNeutralForeground1)] outline-none placeholder:text-[var(--colorNeutralForeground4)]"
            />
            <button
              onClick={submit}
              className="btn-gradient focus-ring inline-flex shrink-0 items-center gap-1.5 rounded-full px-5 py-2.5 text-sm font-semibold"
            >
              Analyze <ArrowRight size={15} />
            </button>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
            {landingQuickPicks.map((q) => (
              <button
                key={q}
                onClick={() => startWith(q)}
                className="focus-ring rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/60 px-3.5 py-1.5 text-[12.5px] font-medium text-[var(--colorNeutralForeground3)] transition-all hover:border-[rgba(15,108,189,0.3)] hover:text-[var(--colorNeutralForeground1)]"
              >
                {q}
              </button>
            ))}
            <button
              onClick={runDemo}
              className="focus-ring inline-flex items-center gap-1.5 rounded-full px-3.5 py-1.5 text-[12.5px] font-semibold text-[var(--colorBrandForeground1)] transition-colors hover:text-[var(--colorBrandForeground2)]"
            >
              <Sparkles size={13} /> Try a sample
            </button>
          </div>
        </motion.div>
      </div>

      {/* Dashboard preview, calm, premium, soft glow */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.26, ease: [0, 0, 0, 1] }}
        className="relative mx-auto mt-16 max-w-5xl"
      >
        <div aria-hidden className="glow left-1/2 top-10 h-[260px] w-[78%] -translate-x-1/2" style={{ background: "radial-gradient(circle, rgba(75,84,200,0.14), transparent 70%)" }} />
        <div className="panel relative overflow-hidden p-2.5">
          <div className="surface-inset flex items-center gap-2 px-4 py-2.5">
            <span className="flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-[#e7e5df]" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#e7e5df]" />
              <span className="h-2.5 w-2.5 rounded-full bg-[#e7e5df]" />
            </span>
            <span className="ml-2 text-[12px] font-medium text-[var(--colorNeutralForeground4)]">Hxrizxn AI · HORIZON-X workspace</span>
          </div>
          <div className="grid gap-2.5 p-2.5 sm:grid-cols-2 lg:grid-cols-4">
            {credibilityItems.map(({ label, icon: Icon, fg, bg }, i) => (
              <div key={label} className="surface-inset bg-white p-4">
                <span className="mb-3 flex h-9 w-9 items-center justify-center rounded-[10px]" style={{ background: bg, color: fg }}>
                  <Icon size={18} />
                </span>
                <div className="text-[13.5px] font-semibold">{label}</div>
                <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-[rgba(0,0,0,0.06)]">
                  <div className="h-full rounded-full" style={{ width: ["72%", "88%", "64%", "94%"][i], background: fg }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* HORIZON-X method */}
      <div className="mt-24">
        <div className="text-center">
          <div className="text-[12px] font-semibold uppercase tracking-[0.22em] text-[var(--colorAccentIndigo)]">The method</div>
          <h2 className="mx-auto mt-3 max-w-2xl text-2xl font-bold tracking-tight md:text-[32px]">
            Eight steps from a tangled choice to one clear next move
          </h2>
        </div>
        <div className="mt-10 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
          {horizonSteps.map(([letter, text], index) => (
            <motion.div
              key={`${letter}-${text}`}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: index * 0.05, duration: 0.35, ease: [0, 0, 0, 1] }}
              className="panel panel--lift p-5"
            >
              <div className="flex items-center justify-between">
                <span
                  className="flex h-10 w-10 items-center justify-center rounded-xl text-base font-bold text-white shadow-[var(--shadow4)]"
                  style={{ background: stepGradients[index % stepGradients.length] }}
                >
                  {letter}
                </span>
                <span className="text-[10px] font-semibold tracking-[0.18em] text-[var(--colorNeutralForeground4)]">
                  STEP {String(index + 1).padStart(2, "0")}
                </span>
              </div>
              <div className="mt-4 text-sm leading-6 text-[var(--colorNeutralForeground2)]">{text}</div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mx-auto mt-14 flex max-w-xl items-center justify-center gap-2 rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/60 px-4 py-2 text-center text-xs text-[var(--colorNeutralForeground3)] backdrop-blur">
        <ShieldCheck size={14} className="shrink-0 text-[var(--colorBrandForeground1)]" />
        Hxrizxn AI is decision support, not a licensed professional.
      </div>
    </section>
  );
}

/* ================================================================
   INTAKE
   ================================================================ */

const sampleVisuals = [
  { icon: Rocket, fg: "#0f6cbd", bg: "#ebf3fc" },
  { icon: Plane, fg: "#5b5fc7", bg: "#eeeffb" },
  { icon: GraduationCap, fg: "#107c10", bg: "#f1faf1" },
  { icon: Home, fg: "#c238b3", bg: "#fbeffa" },
  { icon: Briefcase, fg: "#bc5b09", bg: "#fff9f0" }
];

function FieldShell({
  icon: Icon,
  fg,
  bg,
  label,
  children
}: {
  icon: typeof Target;
  fg: string;
  bg: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="surface-inset p-3.5">
      <div className="mb-2 flex items-center gap-2">
        <span className="flex h-6 w-6 items-center justify-center rounded-md" style={{ background: bg, color: fg }}>
          <Icon size={13} />
        </span>
        <label className="text-xs font-semibold text-[var(--colorNeutralForeground3)]">{label}</label>
      </div>
      {children}
    </div>
  );
}

const inputClass =
  "w-full rounded-lg border border-[var(--colorNeutralStroke2)] bg-white px-3 py-2 text-sm text-[var(--colorNeutralForeground1)] transition-all placeholder:text-[var(--colorNeutralForeground4)] focus:border-[var(--colorBrandStroke1)] focus:outline-none focus:ring-2 focus:ring-[rgba(15,108,189,0.14)]";

function Intake({
  prompt,
  setPrompt,
  goals,
  setGoals,
  fears,
  setFears,
  moneyLimit,
  setMoneyLimit,
  timeHorizon,
  setTimeHorizon,
  runCustom,
  runDemo,
  error
}: {
  prompt: string;
  setPrompt: (value: string) => void;
  goals: string;
  setGoals: (value: string) => void;
  fears: string;
  setFears: (value: string) => void;
  moneyLimit: number;
  setMoneyLimit: (value: number) => void;
  timeHorizon: number;
  setTimeHorizon: (value: number) => void;
  runCustom: () => void;
  runDemo: () => void;
  error: string | null;
}) {
  const sampleDecisions = [
    {
      label: "Should I quit my job and start a startup?",
      prompt: "I'm a software engineer with 3 years of experience. I have savings for 8 months. I want to quit my job and start an AI startup, but I'm worried about burn rate, isolation, and whether I'm romanticizing founder life. Should I quit now, wait 6 months, or test the idea part-time first?",
      goals: "autonomy, learning velocity, avoid regret",
      fears: "burn rate, isolation, no product-market fit",
      moneyLimit: 8,
      timeHorizon: 18
    },
    {
      label: "Should I move to another country?",
      prompt: "Should I move to another country for a new job opportunity, or stay in my home country close to my family and friends?",
      goals: "career growth, adventure, international experience",
      fears: "homesickness, language barrier, visa risk",
      moneyLimit: 6,
      timeHorizon: 12
    },
    {
      label: "Should I pursue graduate school?",
      prompt: "Should I enroll in a full-time Master's program to pivot my career, or continue gaining work experience and learn on the side?",
      goals: "career pivot, deep specialization, credentials",
      fears: "opportunity cost, tuition debt, academic burnout",
      moneyLimit: 12,
      timeHorizon: 24
    },
    {
      label: "Should I buy a house?",
      prompt: "Should I buy a 3-bedroom fixer-upper house in Austin, Texas with a 6.8% mortgage rate requiring $40k in renovations, or keep renting a downtown apartment for the next 2 years to stay mobile?",
      goals: "stability, wealth building, renovation skills",
      fears: "renovation trap, illiquidity, mortgage stress",
      moneyLimit: 24,
      timeHorizon: 36
    },
    {
      label: "Should I switch careers?",
      prompt: "Should I switch from my stable marketing career to a software development role, or continue in my current field where I have seniority?",
      goals: "intellectual challenge, higher salary, industry growth",
      fears: "starting from scratch, ageism, job search fatigue",
      moneyLimit: 6,
      timeHorizon: 12
    }
  ];

  return (
    <section className="mx-auto grid max-w-7xl gap-6 px-6 pb-20 pt-10 lg:grid-cols-[1fr_0.66fr]">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0, 0, 0, 1] }}
        className="panel p-6"
      >
        <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--colorAccentPurple)]">
          <BrainCircuit size={15} />
          Decision Intake
        </div>
        <h1 className="mt-3 text-2xl font-bold tracking-tight md:text-3xl">
          What decision is keeping you up at night?
        </h1>
        <p className="mt-1.5 text-sm text-[var(--colorNeutralForeground3)]">
          Describe it in plain words. The more context you give, the sharper the simulation.
        </p>

        <textarea
          className="focus-ring mt-5 min-h-[220px] w-full resize-y rounded-xl border border-[var(--colorNeutralStroke2)] bg-white p-4 text-sm leading-7 text-[var(--colorNeutralForeground1)] transition-all placeholder:text-[var(--colorNeutralForeground4)] focus:border-[var(--colorBrandStroke1)] focus:outline-none focus:ring-2 focus:ring-[rgba(15,108,189,0.14)]"
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
        />

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <FieldShell icon={Target} fg="#107c10" bg="#f1faf1" label="Goals (comma separated)">
            <input type="text" className={inputClass} value={goals} onChange={(e) => setGoals(e.target.value)} />
          </FieldShell>
          <FieldShell icon={AlertTriangle} fg="#c50f1f" bg="#fdf3f4" label="Fears (comma separated)">
            <input type="text" className={inputClass} value={fears} onChange={(e) => setFears(e.target.value)} />
          </FieldShell>
          <FieldShell icon={Wallet} fg="#bc5b09" bg="#fff9f0" label="Money limit (months)">
            <input
              type="number"
              className={inputClass}
              value={moneyLimit || ""}
              onChange={(e) => setMoneyLimit(Number(e.target.value))}
            />
          </FieldShell>
          <FieldShell icon={Clock} fg="#0f6cbd" bg="#ebf3fc" label="Time horizon (months)">
            <input
              type="number"
              className={inputClass}
              value={timeHorizon || ""}
              onChange={(e) => setTimeHorizon(Number(e.target.value))}
            />
          </FieldShell>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            onClick={runCustom}
            className="btn-gradient focus-ring inline-flex items-center gap-2 rounded-full px-6 py-2.5 text-sm font-semibold"
          >
            Analyze Decision <ArrowRight size={16} />
          </button>
          <button
            onClick={runDemo}
            className="btn-neutral focus-ring rounded-full px-5 py-2.5 text-sm font-semibold"
          >
            Try Sample Decision
          </button>
          <button
            type="button"
            disabled
            aria-disabled="true"
            title="Document upload is coming soon"
            className="inline-flex cursor-not-allowed items-center gap-2 rounded-full border border-[var(--colorNeutralStroke2)] px-4 py-2.5 text-sm text-[var(--colorNeutralForegroundDisabled)]"
          >
            <FileUp size={16} />
            Upload Docs (coming soon)
          </button>
        </div>

        {error && (
          <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-[rgba(197,15,31,0.2)] bg-[var(--colorStatusDangerBackground)] p-3.5 text-sm text-[var(--colorStatusDangerForeground)]">
            <AlertTriangle size={16} className="mt-0.5 shrink-0" />
            {error}
          </div>
        )}
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.08, ease: [0, 0, 0, 1] }}
        className="panel h-fit p-6"
      >
        <h2 className="text-lg font-bold tracking-tight">Sample Decisions</h2>
        <p className="mt-1 text-sm text-[var(--colorNeutralForeground3)]">Not sure where to start? Load one.</p>
        <div className="mt-4 space-y-1.5">
          {sampleDecisions.map((item, index) => {
            const visual = sampleVisuals[index % sampleVisuals.length];
            const Icon = visual.icon;
            return (
              <button
                key={item.label}
                className="focus-ring group flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition-colors hover:bg-[var(--colorSubtleBackgroundHover)]"
                onClick={() => {
                  setPrompt(item.prompt);
                  setGoals(item.goals);
                  setFears(item.fears);
                  setMoneyLimit(item.moneyLimit);
                  setTimeHorizon(item.timeHorizon);
                }}
              >
                <span
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-[10px] transition-transform group-hover:scale-105"
                  style={{ background: visual.bg, color: visual.fg }}
                >
                  <Icon size={17} />
                </span>
                <span className="flex-1 text-sm font-medium text-[var(--colorNeutralForeground2)]">{item.label}</span>
                <ArrowRight
                  size={15}
                  className="shrink-0 text-[var(--colorNeutralForeground4)] transition-transform group-hover:translate-x-1 group-hover:text-[var(--colorBrandForeground1)]"
                />
              </button>
            );
          })}
        </div>
      </motion.div>
    </section>
  );
}

/* ================================================================
   LOADING, gradient progress ring + agent rail
   ================================================================ */

const RING_RADIUS = 56;
const RING_CIRC = 2 * Math.PI * RING_RADIUS;

function Loading({ label, elapsedSec }: { label: string; elapsedSec: number }) {
  const agents = agentLabels;
  const activeIndex = Math.max(0, agents.indexOf(label));
  const progress = (activeIndex + 1) / agents.length;

  return (
    <section className="mx-auto max-w-5xl px-6 pb-20 pt-12">
      <div className="panel relative overflow-hidden p-8 md:p-10">
        <div
          aria-hidden
          className="pointer-events-none absolute -right-28 -top-28 h-80 w-80 rounded-full opacity-50 blur-3xl"
          style={{
            background: "linear-gradient(135deg, rgba(75,84,200,0.40), rgba(15,108,189,0.28))",
            animation: "pulseSoft 4.5s ease-in-out infinite"
          }}
        />

        <div className="relative flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[var(--colorBrandForeground1)]">
            <Activity className="animate-pulse" size={18} />
            Multi-agent pipeline
          </div>
          <span className="rounded-full border border-[rgba(0,0,0,0.06)] bg-white/80 px-3.5 py-1 text-xs font-medium text-[var(--colorNeutralForeground3)]">
            {elapsedSec}s elapsed
          </span>
        </div>

        <h2 className="relative mt-3 text-[28px] font-bold leading-9 tracking-tight">HORIZON-X analysis running</h2>
        <p className="relative mt-2 max-w-2xl text-sm leading-6 text-[var(--colorNeutralForeground3)]">
          Live Azure analysis can take about one to two minutes while each agent generates and validates structured output.
        </p>

        <div className="relative mt-10 grid items-center gap-10 md:grid-cols-[auto_1fr]">
          {/* Progress ring */}
          <div className="relative mx-auto h-[150px] w-[150px]">
            <svg width="150" height="150" viewBox="0 0 150 150" className="-rotate-90">
              <defs>
                <linearGradient id="ring-grad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#0f6cbd" />
                  <stop offset="55%" stopColor="#5b5fc7" />
                  <stop offset="100%" stopColor="#c238b3" />
                </linearGradient>
              </defs>
              <circle cx="75" cy="75" r={RING_RADIUS} stroke="rgba(0,0,0,0.07)" strokeWidth="10" fill="none" />
              <circle
                cx="75"
                cy="75"
                r={RING_RADIUS}
                stroke="url(#ring-grad)"
                strokeWidth="10"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={RING_CIRC}
                strokeDashoffset={RING_CIRC * (1 - progress)}
                style={{ transition: "stroke-dashoffset 900ms var(--curveDecelerateMax)" }}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-bold leading-none">
                {activeIndex + 1}
                <span className="text-base font-semibold text-[var(--colorNeutralForeground4)]">/{agents.length}</span>
              </span>
              <span className="mt-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-[var(--colorNeutralForeground4)]">
                agents
              </span>
            </div>
          </div>

          {/* Current agent + rail */}
          <div>
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, ease: [0, 0, 0, 1] }}
            >
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--colorAccentPurple)]">
                Now running
              </div>
              <div className="mt-1.5 text-xl font-bold tracking-tight md:text-2xl">{label}</div>
              <p className="mt-2 max-w-md text-sm leading-6 text-[var(--colorNeutralForeground3)]">
                {agentBlurbs[activeIndex]}
              </p>
            </motion.div>

            <div className="mt-7 flex flex-wrap gap-2">
              {agents.map((agent, index) => {
                const short = agent.replace(" Agent", "");
                if (index < activeIndex) {
                  return (
                    <span
                      key={agent}
                      className="inline-flex items-center gap-1.5 rounded-full bg-[var(--colorStatusSuccessBackground)] px-3 py-1 text-xs font-medium text-[var(--colorStatusSuccessForeground)]"
                    >
                      <CheckCircle2 size={12} />
                      {short}
                    </span>
                  );
                }
                if (index === activeIndex) {
                  return (
                    <span
                      key={agent}
                      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold text-white"
                      style={{
                        background: "linear-gradient(92deg, #0f6cbd, #5b5fc7)",
                        animation: "pulseSoft 1.6s ease-in-out infinite"
                      }}
                    >
                      <Activity size={12} />
                      {short}
                    </span>
                  );
                }
                return (
                  <span
                    key={agent}
                    className="inline-flex items-center rounded-full border border-[var(--colorNeutralStroke2)] bg-white/60 px-3 py-1 text-xs text-[var(--colorNeutralForeground4)]"
                  >
                    {short}
                  </span>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ================================================================
   COMPARISON
   ================================================================ */

function PanelHeader({ title, caption }: { title: string; caption: string }) {
  return (
    <div className="mb-3 border-b border-[rgba(0,0,0,0.05)] pb-3">
      <div className="text-sm font-bold tracking-tight">{title}</div>
      <p className="mt-0.5 text-xs leading-5 text-[var(--colorNeutralForeground3)]">{caption}</p>
    </div>
  );
}

const scenarioAccents: Record<string, { bar: string; badgeBg: string; badgeFg: string; tag: string }> = {
  optimistic: { bar: "linear-gradient(90deg, #107c10, #54b054)", badgeBg: "#f1faf1", badgeFg: "#107c10", tag: "Upside branch" },
  base: { bar: "linear-gradient(90deg, #0f6cbd, #479ef5)", badgeBg: "#ebf3fc", badgeFg: "#0f6cbd", tag: "Base branch" },
  stress: { bar: "linear-gradient(90deg, #d13438, #ec797d)", badgeBg: "#fdf3f4", badgeFg: "#c50f1f", tag: "Stress branch" }
};

function Comparison({
  data,
  setScreen
}: {
  data: AnalysisPackage;
  setScreen: (screen: "ripple") => void;
}) {
  return (
    <section className="mx-auto max-w-7xl px-6 pb-20 pt-8">
      <SectionHeader icon={Network} eyebrow="Scenario Comparison" title={data.framed_decision.title} />
      <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="panel p-5">
          <PanelHeader
            title="Decision tree"
            caption="Your decision branches into three plausible futures. Green = best case, blue = most likely, red = stress case."
          />
          <ScenarioLattice scenarios={data.scenarios} />
        </div>
        <div className="panel p-5">
          <PanelHeader
            title="Score profile"
            caption="How the three futures compare across five dimensions. A bigger shape means a stronger overall profile."
          />
          <RadarChart data={data} />
        </div>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        {data.scenarios.map((scenario, index) => (
          <ScenarioCard key={scenario.scenario_key} scenario={scenario} index={index} />
        ))}
      </div>
      <NextButton onClick={() => setScreen("ripple")} label="Open Ripple Effects" />
    </section>
  );
}

function ScenarioCard({ scenario, index }: { scenario: ScenarioSpec; index: number }) {
  const accent = scenarioAccents[scenario.scenario_key] ?? scenarioAccents.base;
  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07, duration: 0.4, ease: [0, 0, 0, 1] }}
      className="panel panel--lift overflow-hidden"
    >
      <div className="h-1.5 w-full" style={{ background: accent.bar }} />
      <div className="p-5">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span
            className="rounded-full px-2.5 py-1 text-[11px] font-semibold"
            style={{ background: accent.badgeBg, color: accent.badgeFg }}
          >
            {accent.tag}
          </span>
          <span className="rounded-full border border-[var(--colorNeutralStroke2)] bg-white/70 px-2.5 py-1 text-[11px] font-medium text-[var(--colorNeutralForeground3)]">
            {scenario.probability_band} likely
          </span>
        </div>
        <h3 className="mt-3 text-lg font-bold leading-snug tracking-tight">{scenario.scenario_name}</h3>
        <p className="mt-2.5 min-h-[104px] text-sm leading-6 text-[var(--colorNeutralForeground2)]">{scenario.narrative}</p>
        <div className="mt-4 space-y-2.5 border-t border-[rgba(0,0,0,0.05)] pt-4">
          <ScoreBar label="Upside" value={scenario.upside_score} tone="teal" />
          <ScoreBar label="Downside" value={scenario.downside_score} tone="rose" />
          <ScoreBar label="Regret" value={scenario.regret_score} tone="amber" />
          <ScoreBar label="Reversibility" value={scenario.reversibility_score} tone="violet" />
          <ScoreBar label="Optionality" value={scenario.optionality_score} tone="teal" />
        </div>
      </div>
    </motion.article>
  );
}

/* ================================================================
   RIPPLE
   ================================================================ */

function Ripple({ data, setScreen }: { data: AnalysisPackage; setScreen: (screen: "experiment") => void }) {
  return (
    <section className="mx-auto max-w-7xl px-6 pb-20 pt-8">
      <SectionHeader icon={Waves} eyebrow="Ripple Effects" title="Second-order consequences and risk map" />

      {/* Plain-language explainer */}
      <div className="panel mb-5 flex flex-wrap items-start gap-4 p-5">
        <span
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-white shadow-[var(--shadow4)]"
          style={{ background: "linear-gradient(135deg, #0f6cbd, #5b5fc7)" }}
        >
          <Waves size={20} />
        </span>
        <div className="min-w-[260px] flex-1">
          <div className="text-sm font-bold tracking-tight">What are ripple effects?</div>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-[var(--colorNeutralForeground3)]">
            A decision rarely stops at its first consequence. The maps below trace the knock-on effects of each
            future: which risks show up where, how hard each part of your life gets hit, and how easily you could
            still change course.
          </p>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="panel p-5">
          <PanelHeader
            title="Where the risks live"
            caption="Each row is a risk, each column one of the three futures. Warmer color = more severe. Blank = not a factor."
          />
          <RiskHeatmap data={data} />
        </div>
        <div className="panel p-5">
          <PanelHeader
            title="How the impact cascades"
            caption="Total impact on each life area. 1st order = direct result, 2nd = knock-on effect, 3rd = long-tail consequence."
          />
          <ImpactStack data={data} />
        </div>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
        <div className="panel p-5">
          <PanelHeader
            title="Can you undo it?"
            caption="Each future plotted by how reversible it is and how many doors it keeps open. Top-right is the sweet spot."
          />
          <OptionalityQuadrant data={data} />
        </div>
        <div className="panel p-5">
          <PanelHeader
            title="Behind the scenes"
            caption="The agent pipeline that produced this analysis, with per-agent status and timing."
          />
          <AgentTraceGraph trace={data.trace} />
        </div>
      </div>
      <NextButton onClick={() => setScreen("experiment")} label="Open Experiment Plan" />
    </section>
  );
}

/* ================================================================
   EXPERIMENT
   ================================================================ */

function Experiment({ data, setScreen }: { data: AnalysisPackage; setScreen: (screen: "memo") => void }) {
  const plan = data.experiment_plan;
  return (
    <section className="mx-auto max-w-7xl px-6 pb-20 pt-8">
      <SectionHeader icon={FlaskConical} eyebrow="Experiment Plan" title={plan.plan_name} />
      <div className="grid gap-5 lg:grid-cols-[1fr_0.95fr]">
        <div className="panel p-6">
          <span className="inline-flex items-center gap-2 rounded-full bg-[var(--colorStatusSuccessBackground)] px-3.5 py-1.5 text-sm font-semibold text-[var(--colorStatusSuccessForeground)]">
            <CheckCircle2 size={16} />
            {plan.duration_days} days · reversible
          </span>
          <div className="mt-5 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--colorAccentPurple)]">
            Hypothesis
          </div>
          <p className="mt-2 text-base leading-7 text-[var(--colorNeutralForeground2)]">{plan.hypothesis}</p>

          <div className="mt-7 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--colorBrandForeground1)]">
            Steps
          </div>
          <ol className="mt-4">
            {plan.steps.map((step, index) => (
              <li key={step} className="relative flex gap-4 pb-6 last:pb-0">
                {index < plan.steps.length - 1 && (
                  <span aria-hidden className="absolute bottom-0 left-[14px] top-8 w-px bg-[var(--colorNeutralStroke2)]" />
                )}
                <span
                  className="z-10 flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white shadow-[var(--shadow2)]"
                  style={{ background: "linear-gradient(135deg, #0f6cbd, #5b5fc7)" }}
                >
                  {index + 1}
                </span>
                <span className="pt-0.5 text-sm leading-6 text-[var(--colorNeutralForeground2)]">{step}</span>
              </li>
            ))}
          </ol>
        </div>
        <div className="grid h-fit gap-5">
          <div className="panel p-6">
            <ListBlock title="Success Criteria" items={plan.success_criteria} />
          </div>
          <div className="panel p-6">
            <ListBlock title="Stop Conditions" items={plan.stop_conditions} tone="rose" />
          </div>
          <div className="panel p-6">
            <ListBlock title="What You Will Learn" items={plan.what_you_will_learn} tone="amber" />
          </div>
        </div>
      </div>
      <NextButton onClick={() => setScreen("memo")} label="Open Decision Memo" />
    </section>
  );
}

/* ================================================================
   MEMO
   ================================================================ */

function Memo({ data }: { data: AnalysisPackage; setScreen: (screen: "comparison") => void }) {
  const reportUrl = `${process.env.NEXT_PUBLIC_API_URL || ""}/api/cases/${data.case_id}/report`;
  const citations = useMemo(() => data.memo.citations.slice(0, 4), [data.memo.citations]);
  return (
    <section className="mx-auto max-w-5xl px-6 pb-20 pt-8">
      <SectionHeader icon={ShieldCheck} eyebrow="Decision Memo" title="Proceed via reversible experiment" />

      {/* The recommendation, given headline treatment */}
      <motion.article
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0, 0, 0, 1] }}
        className="panel overflow-hidden"
      >
        <div className="h-1.5 w-full bg-gradient-brand" />
        <div className="p-6 md:p-8">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--colorAccentPurple)]">
            Recommendation
          </div>
          <h2 className="mt-3 max-w-3xl text-xl font-bold leading-relaxed tracking-tight md:text-2xl md:leading-9">
            {data.memo.recommendation_summary}
          </h2>
        </div>
      </motion.article>

      {/* Why, readable column, not a wall */}
      <div className="mt-5 grid gap-5 lg:grid-cols-[1.15fr_0.85fr]">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.07, ease: [0, 0, 0, 1] }}
          className="panel p-6 md:p-7"
        >
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--colorBrandForeground1)]">
            Why this path
          </div>
          <p className="mt-3 text-[15px] leading-7 text-[var(--colorNeutralForeground2)]">{data.memo.rationale}</p>
        </motion.div>

        <div className="grid h-fit gap-5">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.12, ease: [0, 0, 0, 1] }}
            className="panel p-5"
          >
            <div className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--colorStatusWarningBackground)] text-[var(--colorStatusWarningForeground)]">
                <HelpCircle size={16} />
              </span>
              <span className="text-sm font-bold tracking-tight">Still Unknown</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-[var(--colorNeutralForeground2)]">{data.memo.uncertainty_notes}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.17, ease: [0, 0, 0, 1] }}
            className="panel p-5"
          >
            <div className="flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--colorStatusSuccessBackground)] text-[var(--colorStatusSuccessForeground)]">
                <ShieldCheck size={16} />
              </span>
              <span className="text-sm font-bold tracking-tight">Safer Next Move</span>
            </div>
            <p className="mt-3 text-sm leading-6 text-[var(--colorNeutralForeground2)]">{data.memo.safer_next_move}</p>
          </motion.div>
        </div>
      </div>

      <div className="mt-5 flex items-start gap-3 rounded-xl border border-[rgba(15,108,189,0.18)] bg-[var(--colorStatusInfoBackground)] p-4 text-sm leading-6 text-[var(--colorBrandForeground2)]">
        <ShieldCheck size={17} className="mt-0.5 shrink-0" />
        <span>{data.memo.disclaimers}</span>
      </div>

      {citations.length > 0 && (
        <div className="mt-8">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--colorAccentPurple)]">
            Grounded Evidence
          </div>
          <div className="mt-3 grid gap-3 md:grid-cols-2">
            {citations.map((citation) => (
              <div
                key={`${citation.title}-${citation.source}`}
                className="panel panel--lift p-4"
              >
                <div className="text-sm font-bold tracking-tight">{citation.title}</div>
                <div className="mt-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--colorNeutralForeground4)]">
                  {citation.source}
                </div>
                <p className="mt-2 text-sm leading-6 text-[var(--colorNeutralForeground2)]">{citation.snippet}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <a
        className="btn-gradient focus-ring mt-8 inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold"
        href={reportUrl}
        target="_blank"
        rel="noreferrer"
      >
        Export Report <Download size={16} />
      </a>
    </section>
  );
}

/* ================================================================
   SHARED PRIMITIVES
   ================================================================ */

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
    <div className="mb-6 flex flex-wrap items-center justify-between gap-4 border-b border-[var(--colorNeutralStrokeSubtle)] pb-5">
      <div className="flex items-start gap-3.5">
        <span
          className="mt-0.5 flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-[var(--colorNeutralStrokeSubtle)] text-[var(--colorAccentIndigo)]"
          style={{ background: "linear-gradient(135deg, rgba(15,108,189,0.10), rgba(75,84,200,0.10))" }}
        >
          <Icon size={20} />
        </span>
        <div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[var(--colorAccentIndigo)]">
            {eyebrow}
          </div>
          <h1 className="mt-1 text-[26px] font-bold leading-9 tracking-tight md:text-[30px] md:leading-10">{title}</h1>
        </div>
      </div>
      <div className="inline-flex items-center gap-2 rounded-full border border-[var(--colorNeutralStrokeSubtle)] bg-white/70 px-3.5 py-1.5 text-xs font-medium text-[var(--colorNeutralForeground3)] shadow-[var(--shadow2)]">
        <ShieldCheck size={13} className="text-[var(--colorBrandForeground1)]" />
        Decision support, not a licensed professional
      </div>
    </div>
  );
}

const listTones = {
  teal: { fg: "#107c10", bg: "#f1faf1", Icon: CheckCircle2 },
  rose: { fg: "#c50f1f", bg: "#fdf3f4", Icon: XCircle },
  amber: { fg: "#bc5b09", bg: "#fff9f0", Icon: Lightbulb }
};

function ListBlock({ title, items, tone = "teal" }: { title: string; items: string[]; tone?: "teal" | "amber" | "rose" }) {
  const { fg, bg, Icon } = listTones[tone];
  return (
    <div>
      <div className="flex items-center gap-2.5">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg" style={{ background: bg, color: fg }}>
          <Icon size={16} />
        </span>
        <h3 className="text-sm font-bold tracking-tight">{title}</h3>
      </div>
      <ul className="mt-4 space-y-3">
        {items.map((item) => (
          <li key={item} className="flex gap-3 text-sm leading-6 text-[var(--colorNeutralForeground2)]">
            <Icon size={15} className="mt-1 shrink-0" style={{ color: fg }} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function NextButton({ onClick, label }: { onClick: () => void; label: string }) {
  return (
    <div className="mt-7 flex justify-end">
      <button
        onClick={onClick}
        className="btn-gradient focus-ring inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold"
      >
        {label} <ArrowRight size={16} />
      </button>
    </div>
  );
}
