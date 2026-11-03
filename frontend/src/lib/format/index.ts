const NUMBER_FORMATTER = new Intl.NumberFormat('en-IN', {
  maximumFractionDigits: 20,
})
const DATE_FORMATTER = new Intl.DateTimeFormat('en-IN', {
  day: 'numeric',
  month: 'short',
  timeZone: 'UTC',
  year: 'numeric',
})

const LAKH_VALUE = 100_000n
const CRORE_VALUE = 10_000_000n
const COMPACT_PRECISION = 10n

interface ParsedDecimal {
  sign: string
  whole: bigint
  fraction: string
}

function parseDecimal(value: string): ParsedDecimal | null {
  const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(value.trim())
  if (!match) {
    return null
  }

  return {
    sign: match[1] ?? '',
    whole: BigInt(match[2] ?? '0'),
    fraction: match[3] ?? '',
  }
}

function groupDigits(value: string): string {
  const [whole = '', fraction] = value.split('.')
  const lastThree = whole.slice(-3)
  const leading = whole.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',')
  const groupedWhole = leading ? `${leading},${lastThree}` : lastThree
  return fraction === undefined ? groupedWhole : `${groupedWhole}.${fraction}`
}

export function formatIndianNumber(value: number | string): string {
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) {
      return String(value)
    }

    return NUMBER_FORMATTER.format(value)
  }

  const parsed = parseDecimal(value)
  if (!parsed) {
    return value
  }

  const whole = parsed.whole.toString()
  const formatted =
    parsed.fraction.length > 0 ? `${whole}.${parsed.fraction}` : whole
  return `${parsed.sign}${groupDigits(formatted)}`
}

export function formatIndianCurrency(value: number | string): string {
  const formatted = formatIndianNumber(value)
  return formatted.startsWith('-') ? `-₹${formatted.slice(1)}` : `₹${formatted}`
}

function getRoundedTenths(amount: ParsedDecimal, divisor: bigint): bigint {
  const fractionScale = 10n ** BigInt(amount.fraction.length)
  const fractionalAmount = BigInt(amount.fraction || '0')
  const numerator =
    (amount.whole * fractionScale + fractionalAmount) * COMPACT_PRECISION
  const denominator = divisor * fractionScale
  return (numerator + denominator / 2n) / denominator
}

function formatTenths(value: bigint): string {
  const whole = value / COMPACT_PRECISION
  const fraction = value % COMPACT_PRECISION
  return fraction === 0n ? whole.toString() : `${whole}.${fraction}`
}

export function formatIndianCompactCurrency(value: number | string): string {
  const source = String(value).trim()
  const parsed = parseDecimal(source)
  if (!parsed) {
    return formatIndianCurrency(source)
  }

  const unit =
    parsed.whole >= CRORE_VALUE
      ? { divisor: CRORE_VALUE, label: 'Crore' }
      : parsed.whole >= LAKH_VALUE
        ? { divisor: LAKH_VALUE, label: 'Lakh' }
        : null
  if (!unit) {
    return formatIndianCurrency(source)
  }

  const compactValue = formatTenths(getRoundedTenths(parsed, unit.divisor))
  const sign = parsed.sign ? '-' : ''
  return `${sign}₹${compactValue} ${unit.label}`
}

export function formatPercent(value: number | string): string {
  return `${formatIndianNumber(value)}%`
}

export function formatDate(value: Date | string): string {
  const date = value instanceof Date ? value : new Date(value)
  if (!Number.isFinite(date.getTime())) {
    return value instanceof Date ? 'Invalid Date' : value
  }

  return DATE_FORMATTER.format(date)
}
