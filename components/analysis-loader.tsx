"use client"

import { useEffect, useState } from "react"
import { FileSearch, Brain, Calculator, CheckCircle2, Loader2 } from "lucide-react"

const ANALYSIS_STEPS = [
  {
    id: 1,
    label: "Extracting document data",
    description: "Reading tables and text from your PDF",
    icon: FileSearch,
    duration: 5000,
  },
  {
    id: 2,
    label: "AI Analysis",
    description: "Identifying transactions and categories",
    icon: Brain,
    duration: 8000,
  },
  {
    id: 3,
    label: "Calculating insights",
    description: "Computing totals and breakdowns",
    icon: Calculator,
    duration: 4000,
  },
  {
    id: 4,
    label: "Preparing your report",
    description: "Almost there...",
    icon: CheckCircle2,
    duration: 3000,
  },
]

const FUN_FACTS = [
  "The average person makes 35,000 decisions per day. Let us handle your financial ones!",
  "People who track expenses save 20% more on average.",
  "The first credit card was introduced in 1950.",
  "Budgeting can reduce financial stress by up to 50%.",
  "Automation helps 67% of people stick to their savings goals.",
  "The word 'budget' comes from the French word 'bougette' meaning small bag.",
]

export function AnalysisLoader() {
  const [currentStep, setCurrentStep] = useState(0)
  const [funFact, setFunFact] = useState("")
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // Pick a random fun fact
    setFunFact(FUN_FACTS[Math.floor(Math.random() * FUN_FACTS.length)])

    // Simulate progress through steps
    let stepIndex = 0
    const stepTimers: NodeJS.Timeout[] = []

    const advanceStep = () => {
      if (stepIndex < ANALYSIS_STEPS.length - 1) {
        stepIndex++
        setCurrentStep(stepIndex)
        stepTimers.push(setTimeout(advanceStep, ANALYSIS_STEPS[stepIndex].duration))
      }
    }

    stepTimers.push(setTimeout(advanceStep, ANALYSIS_STEPS[0].duration))

    // Progress bar animation
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 95) return prev
        return prev + Math.random() * 2
      })
    }, 200)

    return () => {
      stepTimers.forEach(clearTimeout)
      clearInterval(progressInterval)
    }
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="mx-4 w-full max-w-xl rounded-2xl border bg-card p-8 shadow-2xl">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
          <h3 className="text-xl font-semibold">Analyzing Your Statement</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            This usually takes 15-30 seconds
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mt-6">
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full bg-primary transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="mt-6 space-y-3">
          {ANALYSIS_STEPS.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStep
            const isCompleted = index < currentStep

            return (
              <div
                key={step.id}
                className={`flex items-center gap-3 rounded-lg p-3 transition-all duration-300 ${
                  isActive
                    ? "bg-primary/10 text-primary"
                    : isCompleted
                    ? "text-muted-foreground"
                    : "text-muted-foreground/50"
                }`}
              >
                <div
                  className={`flex h-8 w-8 items-center justify-center rounded-full ${
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : isCompleted
                      ? "bg-green-500 text-white"
                      : "bg-muted"
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-4 w-4" />
                  ) : isActive ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Icon className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${isActive ? "text-primary" : ""}`}>
                    {step.label}
                  </p>
                  {isActive && (
                    <p className="text-xs text-muted-foreground">{step.description}</p>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Fun Fact */}
        <div className="mt-6 rounded-lg bg-muted/50 p-4">
          <p className="text-xs font-medium text-muted-foreground">Did you know?</p>
          <p className="mt-1 text-sm">{funFact}</p>
        </div>
      </div>
    </div>
  )
}
