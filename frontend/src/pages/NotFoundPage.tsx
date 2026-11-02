import { AppLink } from '../components/layout/AppLink'

export function NotFoundPage() {
  return (
    <section className="mx-auto max-w-xl rounded-2xl border border-line bg-surface p-8 text-center">
      <p className="text-sm font-semibold uppercase tracking-widest text-accent">
        404
      </p>
      <h1 className="mt-3 text-2xl font-semibold text-foreground">
        Page not found
      </h1>
      <p className="mt-2 text-muted">
        This address does not match an available page.
      </p>
      <AppLink
        className="mt-6 inline-flex rounded-full bg-accent px-5 py-3 font-semibold text-background transition hover:opacity-85"
        to="/"
      >
        Back to calculators
      </AppLink>
    </section>
  )
}
