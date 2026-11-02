import type {
  AsyncState,
  CalculatorSummary,
} from '../types/calculator'
import { AppLink } from '../components/layout/AppLink'
import { StatusPanel } from '../components/ui/StatusPanel'

interface HomePageProps {
  calculators: AsyncState<CalculatorSummary[]>
}

export function HomePage({ calculators }: HomePageProps) {
  if (calculators.status === 'loading') {
    return (
      <StatusPanel
        message="Calculator list is loading from the backend."
        title="Loading calculators"
      />
    )
  }

  if (calculators.status === 'error') {
    return (
      <StatusPanel
        message={calculators.message}
        title="Could not load calculators"
        tone="error"
      />
    )
  }

  if (calculators.data.length === 0) {
    return (
      <StatusPanel
        message="There are no calculators available yet."
        title="No calculators found"
      />
    )
  }

  const categories = new Map<string, CalculatorSummary[]>()

  for (const calculator of calculators.data) {
    const categoryCalculators = categories.get(calculator.category) ?? []
    categoryCalculators.push(calculator)
    categories.set(calculator.category, categoryCalculators)
  }

  return (
    <div className="space-y-10">
      <section className="max-w-3xl space-y-4">
        <p className="text-sm font-semibold uppercase tracking-widest text-accent">
          Personal finance, made clear
        </p>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Make your next money decision with confidence.
        </h1>
      </section>

      {[...categories].map(([category, items]) => (
        <section className="space-y-4" key={category}>
          <h2 className="text-xl font-semibold text-foreground">{category}</h2>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((calculator) => (
              <AppLink
                className="group rounded-2xl border border-line bg-surface p-5 transition hover:-translate-y-0.5 hover:border-accent/60 hover:bg-surface-raised"
                key={calculator.slug}
                to={`/${encodeURIComponent(calculator.slug)}`}
              >
                <span
                  aria-hidden="true"
                  className="mb-5 inline-flex size-12 items-center justify-center rounded-xl bg-accent-soft text-xl text-accent"
                >
                  {calculator.icon}
                </span>
                <span className="block text-lg font-semibold text-foreground">
                  {calculator.name}
                </span>
                <span className="mt-2 block text-sm text-muted">
                  {calculator.category}
                </span>
              </AppLink>
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}
