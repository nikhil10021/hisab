import type { ReactNode } from 'react'
import type { CalculatorSummary } from '../../types/calculator'
import { AppLink } from './AppLink'

interface AppLayoutProps {
  calculators: CalculatorSummary[]
  children: ReactNode
}

export function AppLayout({ calculators, children }: AppLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b border-line bg-background/85">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <AppLink
              className="text-xl font-bold tracking-tight text-foreground"
              to="/"
            >
              Hisab<span className="text-accent">.</span>
            </AppLink>
            <span className="hidden text-sm text-muted sm:inline">
              Calculators for everyday decisions
            </span>
          </div>
          <nav
            aria-label="Calculators"
            className="flex gap-2 overflow-x-auto pb-1"
          >
            {calculators.map((calculator) => (
              <AppLink
                className="shrink-0 rounded-full border border-line px-3 py-2 text-sm text-muted transition hover:border-accent/60 hover:text-foreground"
                key={calculator.slug}
                to={`/${encodeURIComponent(calculator.slug)}`}
              >
                {calculator.name}
              </AppLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6 sm:py-12 lg:px-8">
        {children}
      </main>
      <footer className="border-t border-line">
        <div className="mx-auto max-w-7xl px-4 py-6 text-sm text-muted sm:px-6 lg:px-8">
          Hisab
        </div>
      </footer>
    </div>
  )
}
