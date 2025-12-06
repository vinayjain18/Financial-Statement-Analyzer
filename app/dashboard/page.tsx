"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowLeft, Download, FileDown, Loader2 } from "lucide-react"
import Link from "next/link"
import { FinancialSummary } from "@/types"
import jsPDF from "jspdf"
import autoTable from "jspdf-autotable"

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

  // Formatter for PDF - uses "Rs." instead of ₹ symbol
  // because jsPDF's default Helvetica font doesn't support the Rupee symbol
  const formatCurrencyForPDF = (amount: number) => {
    return `Rs. ${amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}`
  }

  // Capitalize first letter of a string
  const capitalizeFirst = (str: string) => {
    return str.charAt(0).toUpperCase() + str.slice(1)
  }

  const exportCSV = () => {
    const lines: string[] = []

    // Header section
    lines.push("FinSight - Financial Summary Report")
    lines.push(`Generated on: ${new Date().toLocaleDateString("en-IN")}`)
    lines.push("")

    // Summary section
    lines.push("=== Account Summary ===")
    lines.push(`Opening Balance,${data.openingBalance !== null ? data.openingBalance : "N/A"}`)
    lines.push(`Closing Balance,${data.closingBalance !== null ? data.closingBalance : "N/A"}`)
    lines.push(`Total Income,${data.totalIncome}`)
    lines.push(`Total Expenses,${data.totalExpenses}`)
    lines.push(`Net Change,${data.netChange}`)
    lines.push("")

    // Expense breakdown
    lines.push("=== Expense Breakdown ===")
    lines.push("Category,Amount,Percentage")
    Object.entries(data.categoryBreakdown).forEach(([category, amount]) => {
      const percentage = data.totalExpenses > 0
        ? ((amount / data.totalExpenses) * 100).toFixed(1)
        : "0"
      lines.push(`${capitalizeFirst(category)},${amount},${percentage}%`)
    })
    lines.push("")

    // Income breakdown
    lines.push("=== Income Breakdown ===")
    lines.push("Category,Amount,Percentage")
    if (data.incomeBreakdown) {
      Object.entries(data.incomeBreakdown).forEach(([category, amount]) => {
        const percentage = data.totalIncome > 0
          ? ((amount / data.totalIncome) * 100).toFixed(1)
          : "0"
        lines.push(`${capitalizeFirst(category)},${amount},${percentage}%`)
      })
    }
    lines.push("")

    // Transactions
    lines.push("=== Transaction History ===")
    lines.push("Date,Description,Category,Type,Amount")
    data.transactions.forEach((txn) => {
      // Escape description for CSV (handle commas and quotes)
      const escapedDesc = txn.description.includes(",") || txn.description.includes('"')
        ? `"${txn.description.replace(/"/g, '""')}"`
        : txn.description
      lines.push(`${txn.date},${escapedDesc},${capitalizeFirst(txn.category)},${txn.type},${txn.amount}`)
    })

    // Create and download file
    const csvContent = lines.join("\n")
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.download = `FinSight-Report-${new Date().toISOString().split("T")[0]}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const downloadPDF = () => {
    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    let yPos = 20

    // Title
    doc.setFontSize(20)
    doc.setFont("helvetica", "bold")
    doc.text("FinSight - Financial Summary", pageWidth / 2, yPos, { align: "center" })
    yPos += 10

    // Date
    doc.setFontSize(10)
    doc.setFont("helvetica", "normal")
    doc.text(`Generated on: ${new Date().toLocaleDateString("en-IN")}`, pageWidth / 2, yPos, { align: "center" })
    yPos += 15

    // Account Summary
    doc.setFontSize(14)
    doc.setFont("helvetica", "bold")
    doc.text("Account Summary", 14, yPos)
    yPos += 8

    const summaryData = [
      ["Opening Balance", data.openingBalance !== null ? formatCurrencyForPDF(data.openingBalance) : "N/A"],
      ["Closing Balance", data.closingBalance !== null ? formatCurrencyForPDF(data.closingBalance) : "N/A"],
      ["Total Income", formatCurrencyForPDF(data.totalIncome)],
      ["Total Expenses", formatCurrencyForPDF(data.totalExpenses)],
      ["Net Change", formatCurrencyForPDF(data.netChange)]
    ]

    autoTable(doc, {
      startY: yPos,
      head: [["Metric", "Value"]],
      body: summaryData,
      theme: "striped",
      headStyles: { fillColor: [79, 70, 229] },
      margin: { left: 14, right: 14 }
    })

    yPos = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15

    // Expense Breakdown
    doc.setFontSize(14)
    doc.setFont("helvetica", "bold")
    doc.text("Expense Breakdown", 14, yPos)
    yPos += 8

    const expenseData = Object.entries(data.categoryBreakdown).map(([category, amount]) => {
      const percentage = data.totalExpenses > 0
        ? ((amount / data.totalExpenses) * 100).toFixed(1)
        : "0"
      return [capitalizeFirst(category), formatCurrencyForPDF(amount), `${percentage}%`]
    })

    if (expenseData.length > 0) {
      autoTable(doc, {
        startY: yPos,
        head: [["Category", "Amount", "Percentage"]],
        body: expenseData,
        theme: "striped",
        headStyles: { fillColor: [220, 38, 38] },
        margin: { left: 14, right: 14 }
      })
      yPos = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15
    }

    // Income Breakdown
    doc.setFontSize(14)
    doc.setFont("helvetica", "bold")
    doc.text("Income Breakdown", 14, yPos)
    yPos += 8

    const incomeData = data.incomeBreakdown
      ? Object.entries(data.incomeBreakdown).map(([category, amount]) => {
          const percentage = data.totalIncome > 0
            ? ((amount / data.totalIncome) * 100).toFixed(1)
            : "0"
          return [capitalizeFirst(category), formatCurrencyForPDF(amount), `${percentage}%`]
        })
      : []

    if (incomeData.length > 0) {
      autoTable(doc, {
        startY: yPos,
        head: [["Category", "Amount", "Percentage"]],
        body: incomeData,
        theme: "striped",
        headStyles: { fillColor: [22, 163, 74] },
        margin: { left: 14, right: 14 }
      })
      yPos = (doc as jsPDF & { lastAutoTable: { finalY: number } }).lastAutoTable.finalY + 15
    }

    // Transaction History (new page if needed)
    if (yPos > 200) {
      doc.addPage()
      yPos = 20
    }

    doc.setFontSize(14)
    doc.setFont("helvetica", "bold")
    doc.text(`Transaction History (${data.transactions.length} transactions)`, 14, yPos)
    yPos += 8

    const transactionData = data.transactions.map((txn) => {
      const formattedAmount = txn.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })
      return [
        txn.date,
        txn.description.length > 40 ? txn.description.substring(0, 40) + "..." : txn.description,
        capitalizeFirst(txn.category),
        txn.type === "credit" ? `+${formattedAmount}` : `-${formattedAmount}`
      ]
    })

    autoTable(doc, {
      startY: yPos,
      head: [["Date", "Description", "Category", "Amount"]],
      body: transactionData,
      theme: "striped",
      headStyles: { fillColor: [79, 70, 229] },
      margin: { left: 14, right: 14 },
      columnStyles: {
        0: { cellWidth: 25 },  // Date column
        1: { cellWidth: 65 },  // Description column (reduced to make room for Amount)
        2: { cellWidth: 30 },  // Category column
        3: { cellWidth: 45, halign: "right" }  // Amount column (wider to fit "Rs. X,XX,XXX.XX")
      },
      didParseCell: (hookData) => {
        if (hookData.section === "body" && hookData.column.index === 3) {
          const cellText = hookData.cell.text[0] || ""
          if (cellText.startsWith("+")) {
            hookData.cell.styles.textColor = [22, 163, 74]
          } else if (cellText.startsWith("-")) {
            hookData.cell.styles.textColor = [220, 38, 38]
          }
        }
      }
    })

    // Footer on last page
    const pageCount = (doc as jsPDF & { internal: { getNumberOfPages: () => number } }).internal.getNumberOfPages()
    for (let i = 1; i <= pageCount; i++) {
      doc.setPage(i)
      doc.setFontSize(8)
      doc.setFont("helvetica", "normal")
      doc.text(
        `Page ${i} of ${pageCount} | Generated by FinSight`,
        pageWidth / 2,
        doc.internal.pageSize.getHeight() - 10,
        { align: "center" }
      )
    }

    // Save PDF
    doc.save(`FinSight-Report-${new Date().toISOString().split("T")[0]}.pdf`)
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
            <Button variant="outline" size="sm" onClick={exportCSV}>
              <FileDown className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
            <Button variant="outline" size="sm" onClick={downloadPDF}>
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
