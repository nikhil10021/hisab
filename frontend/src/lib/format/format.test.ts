import { describe, expect, it } from 'vitest'
import {
  formatDate,
  formatIndianCompactCurrency,
  formatIndianCurrency,
  formatIndianNumber,
  formatPercent,
} from './index'

describe('Indian number and currency formatting', () => {
  it('formats zero and grouped rupee values', () => {
    expect(formatIndianNumber('0')).toBe('0')
    expect(formatIndianCurrency('0')).toBe('₹0')
    expect(formatIndianCurrency('1234567.89')).toBe('₹12,34,567.89')
  })

  it('preserves decimals and sign for negative values', () => {
    expect(formatIndianNumber('-123456.75')).toBe('-1,23,456.75')
    expect(formatIndianCurrency('-123456.75')).toBe('-₹1,23,456.75')
  })

  it('uses lakh and crore units for compact currency', () => {
    expect(formatIndianCompactCurrency('0')).toBe('₹0')
    expect(formatIndianCompactCurrency('1250000')).toBe('₹12.5 Lakh')
    expect(formatIndianCompactCurrency('12000000')).toBe('₹1.2 Crore')
    expect(formatIndianCompactCurrency('-12000000')).toBe('-₹1.2 Crore')
  })

  it('retains the compact value precision for very large amounts', () => {
    expect(formatIndianCompactCurrency('12345678901234567890')).toBe(
      '₹1234567890123.5 Crore',
    )
  })

  it('returns invalid numeric strings unchanged', () => {
    expect(formatIndianNumber('not-a-number')).toBe('not-a-number')
    expect(formatIndianCurrency('not-a-number')).toBe('₹not-a-number')
  })
})

describe('percent formatting', () => {
  it('adds a percent sign without scaling zero or positive values', () => {
    expect(formatPercent('0')).toBe('0%')
    expect(formatPercent('12.5')).toBe('12.5%')
  })

  it('formats negative and large percentages', () => {
    expect(formatPercent('-12.5')).toBe('-12.5%')
    expect(formatPercent('123456')).toBe('1,23,456%')
  })
})

describe('date formatting', () => {
  it('formats an ISO date in a stable Indian display format', () => {
    expect(formatDate('2026-01-02')).toBe('2 Jan 2026')
  })

  it('returns invalid date input unchanged', () => {
    expect(formatDate('not-a-date')).toBe('not-a-date')
  })
})
