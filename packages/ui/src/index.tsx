import type { ButtonHTMLAttributes, ReactNode } from "react";

export function IconButton({
  children,
  label,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode; label: string }) {
  return (
    <button aria-label={label} title={label} {...props}>
      {children}
    </button>
  );
}

