import { useParams } from 'react-router-dom'
import { UI_TEXT } from '../constants/uiText'

export function CalculatorPage() {
  const { slug } = useParams()
  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <header className="space-y-3">
        <p className="text-sm font-medium text-accent-primary">
          {UI_TEXT.calculator.title}
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {slug ?? UI_TEXT.calculator.title}
        </h1>
        <p className="max-w-2xl text-muted">{UI_TEXT.calculator.placeholder}</p>
      </header>
    </div>
  )
}
