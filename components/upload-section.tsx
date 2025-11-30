"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Upload, FileText, Lock, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

// In production (Vercel), use empty string for same-origin API calls
// In development, use localhost:8000 for separate Python backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || (typeof window !== "undefined" && window.location.hostname === "localhost" ? "http://localhost:8000" : "")

export function UploadSection() {
  const router = useRouter()
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile)
    } else {
      alert("Please upload a PDF file")
    }
  }, [])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile)
    } else {
      alert("Please upload a PDF file")
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return

    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch(`${API_URL}/api/python/analyze`, {
        method: "POST",
        body: formData,
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || "Failed to analyze statement")
      }

      if (!result.success) {
        throw new Error(result.error || "Failed to analyze statement")
      }

      // Store the result in localStorage and redirect to dashboard
      localStorage.setItem("financialData", JSON.stringify(result.data))
      router.push("/dashboard")
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <section id="upload" className="bg-muted/30 py-20 md:py-32">
      <div className="container">
        <div className="mx-auto max-w-2xl">
          {/* Section Header */}
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Upload Your Statement
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Start analyzing your financial data in seconds
            </p>
          </div>

          {/* Upload Card */}
          <Card className="mt-8">
            <CardContent className="p-6 md:p-8">
              {/* Drag & Drop Zone */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative rounded-lg border-2 border-dashed p-12 text-center transition-colors ${
                  isDragging
                    ? "border-primary bg-primary/5"
                    : "border-muted-foreground/25 hover:border-muted-foreground/50"
                }`}
              >
                <input
                  type="file"
                  accept="application/pdf"
                  onChange={handleFileSelect}
                  className="absolute inset-0 h-full w-full cursor-pointer opacity-0"
                  id="file-upload"
                />

                <div className="space-y-4">
                  {/* Icon */}
                  <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                    {file ? (
                      <FileText className="h-8 w-8 text-primary" />
                    ) : (
                      <Upload className="h-8 w-8 text-primary" />
                    )}
                  </div>

                  {/* Text */}
                  <div>
                    {file ? (
                      <>
                        <p className="text-lg font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </>
                    ) : (
                      <>
                        <p className="text-lg font-medium">
                          Drag & drop your PDF here
                        </p>
                        <p className="text-sm text-muted-foreground">
                          or click to browse
                        </p>
                      </>
                    )}
                  </div>

                  <p className="text-xs text-muted-foreground">
                    PDF only • Max 10MB
                  </p>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="mt-4 rounded-lg bg-red-50 p-4 text-sm text-red-600">
                  {error}
                </div>
              )}

              {/* Upload Button */}
              {file && (
                <div className="mt-6 flex flex-col gap-3">
                  <Button
                    onClick={handleUpload}
                    size="lg"
                    className="w-full"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      "Analyze Statement"
                    )}
                  </Button>
                  <Button
                    onClick={() => {
                      setFile(null)
                      setError(null)
                    }}
                    variant="outline"
                    size="lg"
                    className="w-full"
                    disabled={isLoading}
                  >
                    Choose Different File
                  </Button>
                </div>
              )}

              {/* Sample Statement */}
              <div className="mt-6 text-center">
                <p className="text-sm text-muted-foreground">
                  Don&apos;t have a statement?{" "}
                  <button className="text-primary hover:underline">
                    Download Sample Statement
                  </button>
                </p>
              </div>

              {/* Privacy Notice */}
              <div className="mt-8 flex items-start gap-3 rounded-lg bg-muted/50 p-4">
                <Lock className="h-5 w-5 text-primary mt-0.5" />
                <div className="text-sm text-muted-foreground">
                  <p className="font-medium text-foreground">Your data is safe</p>
                  <p className="mt-1">
                    Your statement is processed securely and never stored on our servers
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
