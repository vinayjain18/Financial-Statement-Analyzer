import { Upload, Sparkles, BarChart3 } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

export function HowItWorksSection() {
  const steps = [
    {
      icon: Upload,
      title: "Upload",
      description: "Upload your bank statement PDF securely",
      step: "1",
    },
    {
      icon: Sparkles,
      title: "Analyze",
      description: "AI extracts and categorizes your transactions automatically",
      step: "2",
    },
    {
      icon: BarChart3,
      title: "Understand",
      description: "View beautiful insights and analytics instantly",
      step: "3",
    },
  ]

  return (
    <section id="how-it-works" className="py-20 md:py-32">
      <div className="container">
        {/* Section Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            How It Works
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Get insights from your financial data in three simple steps
          </p>
        </div>

        {/* Steps Grid */}
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {steps.map((step, index) => {
            const Icon = step.icon
            return (
              <Card key={index} className="relative overflow-hidden">
                <CardContent className="p-6">
                  {/* Step Number */}
                  <div className="absolute right-4 top-4 text-6xl font-bold text-primary/10">
                    {step.step}
                  </div>

                  {/* Icon */}
                  <div className="relative mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold">{step.title}</h3>
                  <p className="mt-2 text-muted-foreground">{step.description}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
