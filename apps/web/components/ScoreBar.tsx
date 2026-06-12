type Props = {
  label: string;
  value: number;
  tone?: "teal" | "amber" | "rose" | "violet";
};

const colors = {
  teal: "linear-gradient(90deg, #107c10, #54b054)",
  amber: "linear-gradient(90deg, #eaa300, #f2c661)",
  rose: "linear-gradient(90deg, #d13438, #ec797d)",
  violet: "linear-gradient(90deg, #5b5fc7, #9ea2f0)"
};

export function ScoreBar({ label, value, tone = "teal" }: Props) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-[var(--colorNeutralForeground3)]">{label}</span>
        <span className="font-semibold text-[var(--colorNeutralForeground1)]">{value}/100</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-[rgba(0,0,0,0.07)]">
        <div
          className="h-full rounded-full"
          style={{
            width: `${value}%`,
            background: colors[tone],
            transition: "width 600ms var(--curveDecelerateMax)"
          }}
        />
      </div>
    </div>
  );
}
