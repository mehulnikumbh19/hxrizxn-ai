import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hxrizxn AI",
  description: "HORIZON-X multi-agent decision simulator for life-changing decisions.",
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

