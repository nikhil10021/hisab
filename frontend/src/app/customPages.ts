import type { ComponentType } from 'react'
import type { CalculatorPageProps } from '../pages/CalculatorPage'
import { IncomeTaxPage } from '../pages/custom/IncomeTaxPage'
import { InflationPage } from '../pages/custom/InflationPage'
import { XirrPage } from '../pages/custom/XirrPage'

export const customPages: Readonly<
  Record<string, ComponentType<CalculatorPageProps>>
> = {
  xirr: XirrPage,
  'xirr-calculator': XirrPage,
  'income-tax': IncomeTaxPage,
  'income-tax-calculator': IncomeTaxPage,
  inflation: InflationPage,
  'inflation-calculator': InflationPage,
}
