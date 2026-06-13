"use client";

import { ShieldCheck, HelpCircle, AlertTriangle } from "lucide-react";
import type { GroundedClaim, RiskItem } from "@/lib/types";

function GroundedBadge() {
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-[var(--colorStatusSuccessBackground)] px-2.5 py-0.5 text-[11px] font-semibold text-[#0e7a0e] ring-1 ring-[rgba(14,122,14,0.1)]">
      <ShieldCheck size={11} /> Grounded
    </span>
  );
}

function UnverifiedBadge() {
  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-[var(--colorStatusWarningBackground)] px-2.5 py-0.5 text-[11px] font-semibold text-[#b3550a] ring-1 ring-[rgba(179,85,10,0.1)]">
      <HelpCircle size={11} /> Unverified
    </span>
  );
}

function sourceLabel(source: string | null): string {
  if (!source) return "";
  const file = source.split("/").pop() ?? source;
  return file.replace(/\.[^.]+$/, "").replace(/-/g, " ");
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="mb-2 flex items-center gap-3">
      <span className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[var(--colorNeutralForeground4)]">
        {children}
      </span>
      <span className="h-px flex-1 bg-[var(--colorNeutralStroke2)]" />
    </div>
  );
}

function ClaimRow({
  text,
  grounded,
  citation,
  blackSwan,
}: {
  text: string;
  grounded: boolean;
  citation?: string | null;
  blackSwan?: boolean;
}) {
  return (
    <div
      className="group flex items-start gap-3 rounded-lg border-l-2 py-2.5 pl-3 pr-2 transition-colors hover:bg-[rgba(0,0,0,0.02)]"
      style={{
        borderLeftColor: grounded
          ? "rgba(14, 122, 14, 0.35)"
          : "rgba(179, 85, 10, 0.35)",
      }}
    >
      <div className="min-w-0 flex-1">
        <p className="text-[12.5px] leading-[1.55] text-[var(--colorNeutralForeground2)]">
          {text}
          {blackSwan && (
            <span className="ml-1.5 inline-flex translate-y-px items-center gap-0.5 text-[10.5px] font-medium text-[#b3550a]">
              <AlertTriangle size={10} />
              black swan
            </span>
          )}
        </p>
        {citation && (
          <span className="mt-0.5 block text-[11px] text-[var(--colorNeutralForeground4)]">
            cites {citation}
          </span>
        )}
      </div>
      {grounded ? <GroundedBadge /> : <UnverifiedBadge />}
    </div>
  );
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
      <div className="mb-4 flex items-center justify-between gap-2">
        <span className="text-[13px] font-semibold text-[var(--colorNeutralForeground1)]">
          Evidence &amp; Honesty
        </span>
        <span className="flex items-baseline gap-1 text-[11px] text-[var(--colorNeutralForeground3)]">
          <span className="text-sm font-bold text-[var(--colorStatusSuccessForeground)]">{groundedCount}</span>
          <span className="font-medium">/{total}</span>
          <span className="font-medium"> grounded in Foundry IQ</span>
        </span>
      </div>

      {assumptions.length > 0 && (
        <div className="mb-4">
          <SectionLabel>Assumptions</SectionLabel>
          <div className="space-y-1">
            {assumptions.map((a, i) => (
              <ClaimRow
                key={`a-${i}`}
                text={a.text}
                grounded={a.status === "grounded"}
                citation={a.status === "grounded" ? a.source_title : null}
              />
            ))}
          </div>
        </div>
      )}

      {risks.length > 0 && (
        <div>
          <SectionLabel>Risks</SectionLabel>
          <div className="space-y-1">
            {risks.map((r, i) => (
              <ClaimRow
                key={`r-${i}`}
                text={r.risk_name}
                grounded={r.grounding_status === "grounded"}
                citation={
                  r.grounding_status === "grounded" && r.grounding_source
                    ? sourceLabel(r.grounding_source)
                    : null
                }
                blackSwan={r.black_swan}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
