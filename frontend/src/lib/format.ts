const indianNumberFormatter = new Intl.NumberFormat('en-IN')
const indianCurrencyFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
})

export function formatIndianNumber(value: number): string {
  return indianNumberFormatter.format(value)
}

export function formatIndianCurrency(value: number): string {
  return indianCurrencyFormatter.format(value)
}
