import {
  Brain,
  Calculator,
  PieChart,
  Download,
  UserX,
  ShieldCheck
} from "lucide-react"

export function FeaturesSection() {
  const features = [
    {
      icon: Brain,
      title: "Smart Transaction Categorization",
      description: "AI automatically categorizes your expenses into meaningful groups",
    },
    {
      icon: Calculator,
      title: "Automated Calculations",
      description: "Accurate balance calculations and spending totals with zero errors",
    },
    {
      icon: PieChart,
      title: "Beautiful Visualizations",
      description: "Interactive charts and graphs that make your data easy to understand",
    },
    {
      icon: Download,
      title: "Export Your Data",
      description: "Download your analyzed data as CSV or PDF for further use",
    },
    {
      icon: UserX,
      title: "No Login Required",
      description: "Start analyzing immediately without creating an account",
    },
    {
      icon: ShieldCheck,
      title: "Privacy First",
      description: "Your data is processed securely and never stored on our servers",
    },
  ]

  return (
    <section id="features" className="bg-muted/30 py-20 md:py-32">
      <div className="container">
        {/* Section Header */}
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl">
            Powerful Features
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Everything you need to understand your financial data
          </p>
        </div>

        {/* Features Grid */}
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="group relative rounded-lg border bg-background p-6 shadow-sm transition-shadow hover:shadow-md"
              >
                {/* Icon */}
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                  <Icon className="h-6 w-6 text-primary" />
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  {feature.description}
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
