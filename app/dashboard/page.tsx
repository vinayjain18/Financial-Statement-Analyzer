"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Download, FileDown, Loader2 } from "lucide-react"
import Link from "next/link"
import { FinancialSummary } from "@/types"

export default function DashboardPage() {
  const router = useRouter()
  const [data, setData] = useState<FinancialSummary | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Load data from localStorage
    const storedData = localStorage.getItem("financialData")
    if (storedData) {
      try {
        setData(JSON.parse(storedData))
      } catch {
        router.push("/")
      }
    } else {
      // No data, redirect to home
      router.push("/")
    }
    setIsLoading(false)
  }, [router])

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!data) {
    return null
  }
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>

          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <FileDown className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Download PDF
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-8">
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Financial Summary</h1>
          <p className="text-muted-foreground">
            Analysis of your bank statement
          </p>
        </div>

        {/* Summary Cards */}
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Opening Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {data.openingBalance !== null ? `₹${data.openingBalance.toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "N/A"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Closing Balance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {data.closingBalance !== null ? `₹${data.closingBalance.toLocaleString("en-IN", { minimumFractionDigits: 2 })}` : "N/A"}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Income
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                +₹{data.totalIncome.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Expenses
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                -₹{data.totalExpenses.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="mb-8 grid gap-8 lg:grid-cols-2">
          {/* Expense Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="text-red-600">Spending by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-[350px] overflow-y-auto">
                {Object.keys(data.categoryBreakdown).length > 0 ? (
                  Object.entries(data.categoryBreakdown).map(
                    ([category, amount]) => {
                      const percentage = data.totalExpenses > 0
                        ? ((amount / data.totalExpenses) * 100).toFixed(1)
                        : "0"
                      return (
                        <div key={category} className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="font-medium capitalize">{category}</span>
                            <span className="text-muted-foreground">
                              ₹{amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })} ({percentage}%)
                            </span>
                          </div>
                          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                            <div
                              className="h-full bg-red-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      )
                    }
                  )
                ) : (
                  <p className="text-muted-foreground text-center py-4">No expenses found</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Income Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle className="text-green-600">Income by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-[350px] overflow-y-auto">
                {data.incomeBreakdown && Object.keys(data.incomeBreakdown).length > 0 ? (
                  Object.entries(data.incomeBreakdown).map(
                    ([category, amount]) => {
                      const percentage = data.totalIncome > 0
                        ? ((amount / data.totalIncome) * 100).toFixed(1)
                        : "0"
                      return (
                        <div key={category} className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className="font-medium capitalize">{category}</span>
                            <span className="text-muted-foreground">
                              ₹{amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })} ({percentage}%)
                            </span>
                          </div>
                          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                            <div
                              className="h-full bg-green-500"
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      )
                    }
                  )
                ) : (
                  <p className="text-muted-foreground text-center py-4">No income found</p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Transaction History */}
        <Card>
          <CardHeader>
            <CardTitle>Transaction History ({data.transactions.length} transactions)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
              <table className="w-full">
                <thead className="sticky top-0 bg-background">
                  <tr className="border-b">
                    <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                      Date
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                      Description
                    </th>
                    <th className="pb-3 text-left text-sm font-medium text-muted-foreground">
                      Category
                    </th>
                    <th className="pb-3 text-right text-sm font-medium text-muted-foreground">
                      Amount
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data.transactions.map((transaction, index) => (
                    <tr key={index} className="hover:bg-muted/50">
                      <td className="py-3 text-sm">{transaction.date}</td>
                      <td className="py-3 text-sm max-w-[300px] truncate" title={transaction.description}>
                        {transaction.description}
                      </td>
                      <td className="py-3 text-sm">
                        <span className="inline-flex rounded-full bg-muted px-2 py-1 text-xs capitalize">
                          {transaction.category}
                        </span>
                      </td>
                      <td
                        className={`py-3 text-right text-sm font-medium ${
                          transaction.type === "credit"
                            ? "text-green-600"
                            : "text-red-600"
                        }`}
                      >
                        {transaction.type === "credit" ? "+" : "-"}₹
                        {transaction.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}
