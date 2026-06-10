type Props = {
  label: string;
  value: number;
  tone?: "teal" | "amber" | "rose" | "violet";
};

const colors = {
  teal: "linear-gradient(90deg, #50e3c2, #9df6df)",
  amber: "linear-gradient(90deg, #f4b95f, #ffe0a3)",
  rose: "linear-gradient(90deg, #ff6b8a, #ff9eb3)",
  violet: "linear-gradient(90deg, #9b5cff, #c6a6ff)"
};

export function ScoreBar({ label, value, tone = "teal" }: Props) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-300">
        <span>{label}</span>
        <span>{value}/100</span>
      </div>
      <div className="h-2 overflow-hidden rounded bg-white/10">
        <div className="h-full rounded" style={{ width: `${value}%`, background: colors[tone] }} />
      </div>
    </div>
  );
}

