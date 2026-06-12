"use client";

import type { ScenarioSpec } from "@/lib/types";

type Branch = { stroke: string; bg: string; fg: string; tag: string };

const branch: Record<string, Branch> = {
  optimistic: { stroke: "#0e7a0e", bg: "#f0f8f0", fg: "#0e7a0e", tag: "Upside branch" },
  base: { stroke: "#0f6cbd", bg: "#eef4fb", fg: "#0f6cbd", tag: "Base branch" },
  stress: { stroke: "#c50f1f", bg: "#fdf3f3", fg: "#c50f1f", tag: "Stress branch" }
};

// Vertical centre (in %) of each branch card, used for the connector curves.
const centerY = [22, 50, 78];
const cardTop = [8, 36, 64];

export function ScenarioLattice({ scenarios }: { scenarios: ScenarioSpec[] }) {
  const items = scenarios.slice(0, 3);

  return (
    <div className="surface-inset relative h-[330px] w-full overflow-hidden">
      {/* Connector layer (drawn behind the cards) */}
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
        aria-hidden
      >
        {items.map((scenario, index) => {
          const accent = branch[scenario.scenario_key] ?? branch.base;
          const y = centerY[index];
          return (
            <path
              key={`${scenario.scenario_key}-${index}`}
              d={`M 23 50 C 35 50, 34 ${y}, 46 ${y}`}
              fill="none"
              stroke={accent.stroke}
              strokeWidth="1.4"
              strokeOpacity="0.55"
              strokeDasharray="3 3"
              vectorEffect="non-scaling-stroke"
            />
          );
        })}
      </svg>

      {/* Decision node */}
      <div className="absolute left-4 top-1/2 z-10 -translate-y-1/2">
        <div
          className="flex h-[60px] w-[116px] flex-col items-center justify-center rounded-xl border text-center shadow-[var(--shadow2)]"
          style={{ background: "linear-gradient(135deg, rgba(15,108,189,0.10), rgba(75,84,200,0.12))", borderColor: "rgba(75,84,200,0.35)" }}
        >
          <span className="text-[13px] font-semibold text-[var(--colorNeutralForeground1)]">Decision</span>
          <span className="mt-0.5 text-[10px] text-[var(--colorNeutralForeground3)]">your choice</span>
        </div>
      </div>

      {/* Branch cards */}
      {items.map((scenario, index) => {
        const accent = branch[scenario.scenario_key] ?? branch.base;
        return (
          <div
            key={`${scenario.scenario_key}-card-${index}`}
            className="absolute right-4 z-10"
            style={{ top: `${cardTop[index]}%`, width: "52%" }}
          >
            <div
              className="rounded-xl border bg-white p-3 shadow-[var(--shadow2)]"
              style={{ borderColor: `${accent.stroke}40` }}
            >
              <div className="flex items-center justify-between gap-2">
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  style={{ background: accent.bg, color: accent.fg }}
                >
                  {accent.tag}
                </span>
                <span className="shrink-0 text-[10px] font-medium text-[var(--colorNeutralForeground3)]">
                  {scenario.probability_band} likely
                </span>
              </div>
              <div className="mt-1.5 line-clamp-2 text-[13px] font-semibold leading-snug text-[var(--colorNeutralForeground1)]">
                {scenario.scenario_name}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
