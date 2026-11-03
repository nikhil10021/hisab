import { useEffect, useState } from 'react'
import { UI_TEXT } from '../../constants/uiText'
import {
  getCalculators,
  getErrorMessage,
  type CalculatorListResponse,
} from './client'

export type CalculatorListState =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'success'; data: CalculatorListResponse }

export function useCalculators(): CalculatorListState {
  const [state, setState] = useState<CalculatorListState>({
    status: 'loading',
  })

  useEffect(() => {
    const controller = new AbortController()

    getCalculators(controller.signal)
      .then((data) => {
        setState({ status: 'success', data })
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return
        }
        setState({
          status: 'error',
          message:
            getErrorMessage(error) ?? UI_TEXT.errors.calculatorListLoadMessage,
        })
      })

    return () => controller.abort()
  }, [])

  return state
}
