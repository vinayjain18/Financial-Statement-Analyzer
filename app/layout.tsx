import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "FinSight - Transform Your Bank Statements Into Actionable Insights",
  description: "Upload your bank statement PDF and get AI-powered analysis with beautiful visualizations. No signup required, 100% secure, and free to use.",
  keywords: ["financial analysis", "bank statement", "AI", "expense tracking", "budgeting"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  );
}
