import { Card, CardContent } from "@/components/ui/card"

export function AboutSection() {
  return (
    <section id="about" className="py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-3xl">
          <Card>
            <CardContent className="p-8 md:p-12">
              {/* Header */}
              <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
                About FinSight
              </h2>

              {/* Content */}
              <div className="mt-6 space-y-4 text-muted-foreground">
                <p className="text-lg leading-relaxed">
                  FinSight is an AI-powered financial statement analyzer that helps you
                  understand your spending patterns and financial health in seconds.
                </p>

                <p className="leading-relaxed">
                  Simply upload your bank statement PDF, and our advanced AI will extract
                  all transactions, categorize them intelligently, and present you with
                  beautiful visualizations and actionable insights.
                </p>

                <p className="leading-relaxed">
                  We built FinSight with privacy and simplicity in mind. Your data is
                  processed securely and never stored on our servers. No account creation,
                  no complicated setup—just instant insights.
                </p>
              </div>

              {/* Tech Stack */}
              <div className="mt-8 rounded-lg bg-muted/50 p-6">
                <h3 className="font-semibold">Powered By</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  Next.js, FastAPI, OpenAI GPT-4, and advanced PDF extraction technology
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
