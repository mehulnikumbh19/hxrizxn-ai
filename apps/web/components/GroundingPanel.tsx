"use client";

import { ShieldCheck, HelpCircle } from "lucide-react";
import type { GroundedClaim, RiskItem } from "@/lib/types";

/**
 * Cite-or-abstain panel. Every claim is shown either as GROUNDED (with the
 * Foundry IQ source it was verified against) or UNVERIFIED (the agent abstains
 * from asserting it as fact). This is the trust surface that distinguishes a
 * real reasoning agent from one that confidently guesses.
 */

function GroundedBadge() {
  return (
    <span
      className="inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold"
      style={{ background: "var(--colorStatusSuccessBackground)", color: "#0e7a0e" }}
    >
      <ShieldCheck size={11} /> Grounded
    </span>
  );
}

function UnverifiedBadge() {
  return (
    <span
      className="inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-semibold"
      style={{ background: "var(--colorStatusWarningBackground)", color: "#b3550a" }}
    >
      <HelpCircle size={11} /> Unverified
    </span>
  );
}

function sourceLabel(source: string | null): string {
  if (!source) return "";
  // demo-data/startup-idea-note.md -> startup-idea-note
  const file = source.split("/").pop() ?? source;
  return file.replace(/\.[^.]+$/, "");
}

export function GroundingPanel({
  assumptions,
  risks,
}: {
  assumptions: GroundedClaim[];
  risks: RiskItem[];
}) {
  const groundedCount =
    assumptions.filter((a) => a.status === "grounded").length +
    risks.filter((r) => r.grounding_status === "grounded").length;
  const total = assumptions.length + risks.length;

  return (
    <div className="surface-inset p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <span className="text-[13px] font-semibold text-[var(--colorNeutralForeground1)]">
          Evidence &amp; Honesty
        </span>
        <span className="text-[11px] font-medium text-[var(--colorNeutralForeground3)]">
          {groundedCount}/{total} grounded in Foundry IQ
        </span>
      </div>

      {assumptions.length > 0 && (
        <div className="mb-4">
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-[var(--colorNeutralForeground3)]">
            Assumptions
          </p>
          <ul className="space-y-2">
            {assumptions.map((a, i) => (
              <li key={`a-${i}`} className="flex items-start justify-between gap-3">
                <span className="text-[12px] text-[var(--colorNeutralForeground2)]">
                  {a.text}
                  {a.status === "grounded" && a.source_title && (
                    <span className="mt-0.5 block text-[11px] text-[var(--colorNeutralForeground3)]">
                      cites {a.source_title}
                    </span>
                  )}
                </span>
                {a.status === "grounded" ? <GroundedBadge /> : <UnverifiedBadge />}
              </li>
            ))}
          </ul>
        </div>
      )}

      {risks.length > 0 && (
        <div>
          <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-[var(--colorNeutralForeground3)]">
            Risks
          </p>
          <ul className="space-y-2">
            {risks.map((r, i) => (
              <li key={`r-${i}`} className="flex items-start justify-between gap-3">
                <span className="text-[12px] text-[var(--colorNeutralForeground2)]">
                  {r.risk_name}
                  {r.black_swan && (
                    <span className="ml-1.5 text-[11px] font-medium" style={{ color: "#b3550a" }}>
                      (black swan)
                    </span>
                  )}
                  {r.grounding_status === "grounded" && r.grounding_source && (
                    <span className="mt-0.5 block text-[11px] text-[var(--colorNeutralForeground3)]">
                      cites {sourceLabel(r.grounding_source)}
                    </span>
                  )}
                </span>
                {r.grounding_status === "grounded" ? <GroundedBadge /> : <UnverifiedBadge />}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
