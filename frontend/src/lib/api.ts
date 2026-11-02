import type {
  CalculationRequest,
  CalculationResponse,
  CalculatorSchema,
  CalculatorSummary,
  JsonObject,
  JsonValue,
} from '../types/calculator'

class ApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

function getApiUrl(path: string): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/+$/, '')

  if (!baseUrl) {
    throw new ApiError('API URL is not configured. Set VITE_API_BASE_URL to connect.')
  }

  return `${baseUrl}/api/${path}`
}

function isJsonValue(value: unknown): value is JsonValue {
  if (
    value === null ||
    typeof value === 'string' ||
    typeof value === 'number' ||
    typeof value === 'boolean'
  ) {
    return true
  }

  if (Array.isArray(value)) {
    return value.every(isJsonValue)
  }

  return isJsonObject(value)
}

function isJsonObject(value: unknown): value is JsonObject {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    return false
  }

  return Object.values(value).every(isJsonValue)
}

function isCalculatorSummary(value: unknown): value is CalculatorSummary {
  if (!isJsonObject(value)) {
    return false
  }

  return (
    typeof value.slug === 'string' &&
    typeof value.name === 'string' &&
    typeof value.category === 'string' &&
    typeof value.icon === 'string'
  )
}

async function requestJson(
  path: string,
  init?: RequestInit,
): Promise<unknown> {
  let response: Response

  try {
    response = await fetch(getApiUrl(path), init)
  } catch (error) {
    if (error instanceof TypeError) {
      throw new ApiError('Could not connect to the backend. Please try again later.')
    }

    throw error
  }

  if (!response.ok) {
    throw new ApiError(`The backend could not complete the request (${response.status}).`)
  }

  try {
    const payload: unknown = await response.json()
    return payload
  } catch (error) {
    if (error instanceof SyntaxError) {
      throw new ApiError('The backend returned an invalid response.')
    }

    throw error
  }
}

export async function getCalculators(): Promise<CalculatorSummary[]> {
  const payload = await requestJson('calculators')
  const list = Array.isArray(payload)
    ? payload
    : isJsonObject(payload) && Array.isArray(payload.calculators)
      ? payload.calculators
      : null

  if (!list || !list.every(isCalculatorSummary)) {
    throw new ApiError('The backend returned an invalid calculator list.')
  }

  return list
}

export async function getCalculator(slug: string): Promise<CalculatorSchema> {
  const payload = await requestJson(`calculators/${encodeURIComponent(slug)}`)

  if (!isJsonObject(payload)) {
    throw new ApiError('The backend returned an invalid calculator schema.')
  }

  return payload
}

export async function postCalculator(
  slug: string,
  input: CalculationRequest,
): Promise<CalculationResponse> {
  const payload = await requestJson(
    `calculators/${encodeURIComponent(slug)}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    },
  )

  if (!isJsonObject(payload)) {
    throw new ApiError('The backend returned an invalid calculation result.')
  }

  return payload
}
