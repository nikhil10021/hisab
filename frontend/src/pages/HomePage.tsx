import { Link, useSearchParams } from 'react-router-dom'
import type { CalculatorListResponse } from '../lib/api/client'
import { UI_TEXT } from '../constants/uiText'
import { useCalculators } from '../lib/api/useCalculators'
import { StatusPanel } from '../components/ui/StatusPanel'

export function HomePage() {
  const calculators = useCalculators()
  const [searchParams] = useSearchParams()
  const searchTerm = (searchParams.get('q') ?? '').trim().toLocaleLowerCase()

  if (calculators.status === 'loading') {
    return (
      <StatusPanel
        message={UI_TEXT.errors.calculatorListLoadingMessage}
        title={UI_TEXT.errors.calculatorListLoadingTitle}
      />
    )
  }

  if (calculators.status === 'error') {
    return (
      <StatusPanel
        message={calculators.message}
        title={UI_TEXT.errors.calculatorListLoadTitle}
        tone="error"
      />
    )
  }

  const categories = new Map<string, CalculatorListResponse>()

  const filteredCalculators = calculators.data.filter((calculator) =>
    [calculator.name, calculator.description, calculator.category].some(
      (value) => value.toLocaleLowerCase().includes(searchTerm),
    ),
  )

  for (const calculator of filteredCalculators) {
    const categoryCalculators = categories.get(calculator.category) ?? []
    categoryCalculators.push(calculator)
    categories.set(calculator.category, categoryCalculators)
  }

  return (
    <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_20rem]">
      <aside className="order-1 space-y-5 lg:col-start-2 lg:row-start-1">
        <h1 className="text-xl font-semibold text-foreground">
          {UI_TEXT.home.calculatorListTitle}
        </h1>
        {calculators.data.length === 0 ? (
          <StatusPanel
            message={UI_TEXT.home.emptyMessage}
            title={UI_TEXT.home.emptyTitle}
          />
        ) : categories.size === 0 ? (
          <StatusPanel
            message={UI_TEXT.home.noSearchResultsMessage}
            title={UI_TEXT.home.noSearchResultsTitle}
          />
        ) : (
          [...categories].map(([category, items]) => (
            <details
              className="group rounded-xl border border-line bg-surface"
              key={category}
              open
            >
              <summary className="cursor-pointer list-none px-4 py-3 font-semibold text-foreground marker:hidden">
                {category}
              </summary>
              <ul className="space-y-1 px-2 pb-2">
                {items.map((calculator) => (
                  <li key={calculator.slug}>
                    <Link
                      className="block rounded-lg px-3 py-2 text-sm text-muted hover:bg-surface-raised hover:text-foreground motion-reduce:transition-none"
                      to={`/calculators/${encodeURIComponent(calculator.slug)}`}
                    >
                      {calculator.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </details>
          ))
        )}
      </aside>

      <section className="order-2 max-w-3xl space-y-4 lg:col-start-1 lg:row-start-1 lg:self-center">
        <p className="text-sm font-semibold uppercase tracking-widest text-accent-primary">
          {UI_TEXT.home.eyebrow}
        </p>
        <h2 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          {UI_TEXT.home.title}
        </h2>
        <p className="max-w-2xl text-muted">{UI_TEXT.home.description}</p>
      </section>
    </div>
  )
}
