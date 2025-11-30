// Financial statement analysis types

export interface Transaction {
  date: string
  description: string
  category: string
  amount: number
  type: "credit" | "debit"
}

export interface CategoryBreakdown {
  [category: string]: number
}

export interface FinancialSummary {
  openingBalance: number | null
  closingBalance: number | null
  totalIncome: number
  totalExpenses: number
  netChange: number
  transactions: Transaction[]
  categoryBreakdown: CategoryBreakdown
  incomeBreakdown: CategoryBreakdown
  transactionCount?: number
}

export interface UploadResponse {
  success: boolean
  data?: FinancialSummary
  error?: string
}
