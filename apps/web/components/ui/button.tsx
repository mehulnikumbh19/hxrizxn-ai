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
    primary: "bg-white text-slate-950 hover:bg-slate-200",
    secondary: "border border-white/20 bg-black/30 text-white hover:bg-white/10",
    ghost: "text-slate-300 hover:bg-white/10"
  };
  return (
    <button
      className={cn("focus-ring inline-flex items-center justify-center gap-2 rounded px-5 py-3 font-semibold", variants[variant], className)}
      {...props}
    >
      {children}
    </button>
  );
}

