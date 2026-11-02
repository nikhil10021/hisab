import { useEffect, useState } from 'react'
import { StatusPanel } from '../components/ui/StatusPanel'
import { getCalculator } from '../lib/api'
import type {
  AsyncState,
  CalculatorSchema,
  CalculatorSummary,
} from '../types/calculator'

export interface CalculatorPageProps {
  slug: string
  calculator: CalculatorSummary
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'Something went wrong while loading this calculator.'
}

export function CalculatorPage({ slug, calculator }: CalculatorPageProps) {
  const [schema, setSchema] = useState<AsyncState<CalculatorSchema>>({
    status: 'loading',
  })

  useEffect(() => {
    let active = true

    getCalculator(slug)
      .then((data) => {
        if (active) {
          setSchema({ status: 'success', data })
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setSchema({ status: 'error', message: getErrorMessage(error) })
        }
      })

    return () => {
      active = false
    }
  }, [slug])

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <p className="text-sm font-medium text-accent">{calculator.category}</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">
          {calculator.name}
        </h1>
      </div>
      {schema.status === 'loading' && (
        <StatusPanel
          message="Loading the calculator schema from the backend."
          title="Loading calculator"
        />
      )}
      {schema.status === 'error' && (
        <StatusPanel
          message={schema.message}
          title="Could not load calculator"
          tone="error"
        />
      )}
      {schema.status === 'success' && (
        <StatusPanel
          message="The schema is ready. Calculator inputs will be added later."
          title="Calculator ready"
        />
      )}
    </div>
  )
}
