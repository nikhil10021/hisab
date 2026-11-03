import type { paths } from './generated'
import { UI_TEXT } from '../../constants/uiText'

export type CalculatorListResponse =
  paths['/api/v1/calculators']['get']['responses'][200]['content']['application/json']

type JsonRecord = Record<string, unknown>

function isJsonRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function getApiBaseUrl(): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.trim().replace(/\/+$/, '')
  if (!baseUrl) {
    throw new Error(UI_TEXT.errors.apiConnectionFailed)
  }
  return baseUrl
}

async function requestJson<ResponseBody>(
  path: string,
  signal: AbortSignal,
): Promise<ResponseBody> {
  let response: Response
  try {
    response = await fetch(`${getApiBaseUrl()}/api/v1/${path}`, { signal })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw error
    }
    if (error instanceof TypeError) {
      throw new Error(UI_TEXT.errors.apiConnectionFailed, { cause: error })
    }
    throw error
  }

  let payload: unknown
  try {
    payload = await response.json()
  } catch (error) {
    if (!(error instanceof SyntaxError)) {
      throw error
    }
    if (response.ok) {
      throw new Error(UI_TEXT.errors.invalidApiResponse, { cause: error })
    }
  }

  if (!response.ok) {
    if (
      isJsonRecord(payload) &&
      typeof payload.code === 'string' &&
      typeof payload.message === 'string' &&
      'details' in payload
    ) {
      throw payload
    }
    throw new Error(UI_TEXT.errors.apiRequestFailed)
  }

  return payload as ResponseBody
}

export function getErrorMessage(error: unknown): string | undefined {
  if (error instanceof Error) {
    return error.message
  }
  if (isJsonRecord(error) && typeof error.message === 'string') {
    return error.message
  }
  return undefined
}

export function getCalculators(
  signal: AbortSignal,
): Promise<CalculatorListResponse> {
  return requestJson<CalculatorListResponse>('calculators', signal)
}
