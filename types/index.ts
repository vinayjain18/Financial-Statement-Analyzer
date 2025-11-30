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
  openingBalance: number
  closingBalance: number
  totalIncome: number
  totalExpenses: number
  netChange: number
  transactions: Transaction[]
  categoryBreakdown: CategoryBreakdown
  spendingPercentage?: {
    [category: string]: number
  }
}

export interface UploadResponse {
  success: boolean
  data?: FinancialSummary
  error?: string
}
