"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight, Shield, Zap, Lock } from "lucide-react"

export function HeroSection() {
  const scrollToUpload = () => {
    const element = document.getElementById("upload")
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <section id="home" className="relative overflow-hidden py-20 md:py-32">
      {/* Background gradient */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-primary/5 via-background to-background" />

      <div className="container">
        <div className="mx-auto max-w-4xl text-center">
          {/* Main Headline */}
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl md:text-7xl">
            Transform Your Bank Statements Into{" "}
            <span className="text-primary">Actionable Insights</span>
          </h1>

          {/* Subheadline */}
          <p className="mt-6 text-lg leading-8 text-muted-foreground md:text-xl">
            Upload. Analyze. Understand. All in seconds.
            <br />
            AI-powered financial analysis with beautiful visualizations.
          </p>

          {/* CTA Button */}
          <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:justify-center">
            <Button onClick={scrollToUpload} size="lg" className="text-base">
              Analyze Your Statement
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Trust Badges */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              <span>No signup required</span>
            </div>
            <div className="flex items-center gap-2">
              <Lock className="h-4 w-4 text-primary" />
              <span>100% secure</span>
            </div>
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              <span>Free to use</span>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="mt-16 rounded-xl border bg-background p-4 shadow-2xl">
            <div className="space-y-3">
              {/* Mini Summary Cards */}
              <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
                <div className="rounded-lg border bg-card p-3">
                  <p className="text-xs text-muted-foreground">Opening Balance</p>
                  <p className="text-lg font-bold">$5,000</p>
                </div>
                <div className="rounded-lg border bg-card p-3">
                  <p className="text-xs text-muted-foreground">Closing Balance</p>
                  <p className="text-lg font-bold">$4,235</p>
                </div>
                <div className="rounded-lg border bg-card p-3">
                  <p className="text-xs text-muted-foreground">Total Income</p>
                  <p className="text-lg font-bold text-green-600">+$2,500</p>
                </div>
                <div className="rounded-lg border bg-card p-3">
                  <p className="text-xs text-muted-foreground">Total Expenses</p>
                  <p className="text-lg font-bold text-red-600">-$3,265</p>
                </div>
              </div>

              {/* Mini Charts Preview */}
              <div className="grid gap-2 md:grid-cols-2">
                <div className="rounded-lg border bg-card p-3">
                  <p className="mb-2 text-sm font-semibold">Spending by Category</p>
                  <div className="space-y-2">
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Groceries</span>
                        <span>$450</span>
                      </div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div className="h-full bg-primary" style={{ width: "35%" }} />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Utilities</span>
                        <span>$200</span>
                      </div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div className="h-full bg-primary" style={{ width: "20%" }} />
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Entertainment</span>
                        <span>$150</span>
                      </div>
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                        <div className="h-full bg-primary" style={{ width: "15%" }} />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="rounded-lg border bg-card p-3">
                  <p className="mb-2 text-sm font-semibold">Recent Transactions</p>
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Salary Deposit</span>
                      <span className="font-medium text-green-600">+$2,500</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Walmart Purchase</span>
                      <span className="font-medium text-red-600">-$125</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Netflix Subscription</span>
                      <span className="font-medium text-red-600">-$16</span>
                    </div>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted-foreground">Electric Bill</span>
                      <span className="font-medium text-red-600">-$85</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
