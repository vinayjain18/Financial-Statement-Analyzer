"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Download, FileDown } from "lucide-react"
import Link from "next/link"

// Mock data - will be replaced with real data from API
const mockData = {
  openingBalance: 5000.0,
  closingBalance: 4235.5,
  totalIncome: 2500.0,
  totalExpenses: 3264.5,
  netChange: -764.5,
  transactions: [
    {
      date: "2025-01-15",
      description: "Salary Deposit",
      category: "Income",
      amount: 2500.0,
      type: "credit",
    },
    {
      date: "2025-01-16",
      description: "Walmart Purchase",
      category: "Groceries",
      amount: -125.5,
      type: "debit",
    },
    {
      date: "2025-01-17",
      description: "Netflix Subscription",
      category: "Entertainment",
      amount: -15.99,
      type: "debit",
    },
    {
      date: "2025-01-18",
      description: "Electric Bill",
      category: "Utilities",
      amount: -85.0,
      type: "debit",
    },
  ],
  categoryBreakdown: {
    Groceries: 450.75,
    Utilities: 200.0,
    Entertainment: 150.0,
    Dining: 300.25,
    Transportation: 125.0,
    Other: 2038.5,
  },
}

export default function DashboardPage() {
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
                ${mockData.openingBalance.toFixed(2)}
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
                ${mockData.closingBalance.toFixed(2)}
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
                +${mockData.totalIncome.toFixed(2)}
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
                -${mockData.totalExpenses.toFixed(2)}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="mb-8 grid gap-8 lg:grid-cols-2">
          {/* Category Breakdown */}
          <Card>
            <CardHeader>
              <CardTitle>Spending by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(mockData.categoryBreakdown).map(
                  ([category, amount]) => {
                    const percentage = (
                      (amount / mockData.totalExpenses) *
                      100
                    ).toFixed(1)
                    return (
                      <div key={category} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium">{category}</span>
                          <span className="text-muted-foreground">
                            ${amount.toFixed(2)} ({percentage}%)
                          </span>
                        </div>
                        <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                          <div
                            className="h-full bg-primary"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    )
                  }
                )}
              </div>
            </CardContent>
          </Card>

          {/* Placeholder for Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Monthly Trend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex h-[300px] items-center justify-center rounded-lg bg-muted/30">
                <p className="text-muted-foreground">Chart coming soon</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Transaction History */}
        <Card>
          <CardHeader>
            <CardTitle>Transaction History</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
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
                  {mockData.transactions.map((transaction, index) => (
                    <tr key={index} className="hover:bg-muted/50">
                      <td className="py-3 text-sm">{transaction.date}</td>
                      <td className="py-3 text-sm">{transaction.description}</td>
                      <td className="py-3 text-sm">
                        <span className="inline-flex rounded-full bg-muted px-2 py-1 text-xs">
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
                        {transaction.type === "credit" ? "+" : ""}$
                        {Math.abs(transaction.amount).toFixed(2)}
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
