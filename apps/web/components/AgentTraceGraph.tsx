"use client";

import { Activity, CheckCircle2 } from "lucide-react";
import type { AgentTraceView } from "@/lib/types";

export function AgentTraceGraph({ trace }: { trace: AgentTraceView[] }) {
  return (
    <div className="surface-inset h-[350px] overflow-y-auto p-4">
      <ol className="relative">
        {trace.map((item, index) => {
          const completed = item.status === "completed";
          const accent = completed ? "#0e7a0e" : "#b3550a";
          const badgeBg = completed ? "var(--colorStatusSuccessBackground)" : "var(--colorStatusWarningBackground)";
          const isLast = index === trace.length - 1;
          return (
            <li key={`${item.agent_name}-${index}`} className="relative flex gap-3 pb-3.5 last:pb-0">
              {!isLast && (
                <span
                  aria-hidden
                  className="absolute bottom-0 left-[11px] top-6 w-px"
                  style={{ background: "var(--colorNeutralStroke2)" }}
                />
              )}
              <span
                className="z-10 mt-0.5 flex h-[22px] w-[22px] shrink-0 items-center justify-center rounded-full"
                style={{ background: badgeBg, color: accent }}
              >
                {completed ? <CheckCircle2 size={13} /> : <Activity size={13} />}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-[13px] font-semibold text-[var(--colorNeutralForeground1)]">
                    {item.agent_name}
                  </span>
                  <span className="shrink-0 text-[11px] font-medium text-[var(--colorNeutralForeground3)]">
                    {item.latency_ms} ms
                  </span>
                </div>
                <span
                  className="mt-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize"
                  style={{ background: badgeBg, color: accent }}
                >
                  {item.status}
                </span>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
