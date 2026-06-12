import type { ButtonHTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

type Variant = "primary" | "secondary" | "ghost";

export function Button({
  children,
  className,
  variant = "primary",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode; variant?: Variant }) {
  const variants = {
    primary:
      "bg-[var(--colorBrandBackground)] text-white hover:bg-[var(--colorBrandBackgroundHover)] active:bg-[var(--colorBrandBackgroundPressed)]",
    secondary:
      "border border-[var(--colorNeutralStrokeAccessible)] bg-transparent text-[var(--colorNeutralForeground1)] hover:bg-[var(--colorSubtleBackgroundHover)] active:bg-[var(--colorSubtleBackgroundPressed)]",
    ghost:
      "bg-transparent border-none text-[var(--colorNeutralForeground2)] hover:bg-[var(--colorSubtleBackgroundHover)] active:bg-[var(--colorSubtleBackgroundPressed)]"
  };
  return (
    <button
      className={cn(
        "focus-ring inline-flex items-center justify-center gap-2 rounded-[var(--borderRadiusMedium)] px-4 py-2 text-sm font-semibold min-h-[32px] transition-all duration-[var(--durationFast)] disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
