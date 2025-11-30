"use client"

import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

export function Header() {
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id)
    if (element) {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <span className="text-lg font-bold text-primary-foreground">F</span>
          </div>
          <span className="text-xl font-bold">FinSight</span>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <button
            onClick={() => scrollToSection("home")}
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Home
          </button>
          <button
            onClick={() => scrollToSection("how-it-works")}
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            How It Works
          </button>
          <button
            onClick={() => scrollToSection("features")}
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            Features
          </button>
          <button
            onClick={() => scrollToSection("about")}
            className="text-sm font-medium transition-colors hover:text-primary"
          >
            About
          </button>
        </nav>

        {/* CTA Button */}
        <Button
          onClick={() => scrollToSection("upload")}
          size="lg"
          className="hidden md:inline-flex"
        >
          Analyze Statement
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>

        {/* Mobile CTA */}
        <Button
          onClick={() => scrollToSection("upload")}
          size="default"
          className="md:hidden"
        >
          Analyze
        </Button>
      </div>
    </header>
  )
}
