export type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | JsonObject

export interface JsonObject {
  [key: string]: JsonValue
}

export interface CalculatorSummary {
  slug: string
  name: string
  category: string
  icon: string
}

export type CalculatorSchema = JsonObject
export type CalculationRequest = JsonObject
export type CalculationResponse = JsonObject

export type AsyncState<T> =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; data: T }
