export function Footer() {
  return (
    <footer className="border-t bg-muted/50">
      <div className="container py-8 md:py-12">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <span className="text-lg font-bold text-primary-foreground">F</span>
              </div>
              <span className="text-xl font-bold">FinSight</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Transform your bank statements into actionable insights with AI-powered analysis.
            </p>
          </div>

          {/* Links - Placeholder for future */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <button className="hover:text-foreground transition-colors">
                  How It Works
                </button>
              </li>
              <li>
                <button className="hover:text-foreground transition-colors">
                  Features
                </button>
              </li>
              <li>
                <button className="hover:text-foreground transition-colors">
                  Privacy
                </button>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold">Legal</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <button className="hover:text-foreground transition-colors">
                  Privacy Policy
                </button>
              </li>
              <li>
                <button className="hover:text-foreground transition-colors">
                  Terms of Use
                </button>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>© 2025 FinSight. Built with AI.</p>
        </div>
      </div>
    </footer>
  )
}
