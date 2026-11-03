import { Link } from 'react-router-dom'
import { UI_TEXT } from '../constants/uiText'

export function NotFoundPage() {
  return (
    <section className="mx-auto max-w-xl rounded-2xl border border-line bg-surface p-8 text-center">
      <h1 className="mt-3 text-2xl font-semibold text-foreground">
        {UI_TEXT.errors.pageNotFoundTitle}
      </h1>
      <p className="mt-2 text-muted">{UI_TEXT.errors.pageNotFoundMessage}</p>
      <Link
        className="mt-6 inline-flex rounded-full bg-accent-primary px-5 py-3 font-semibold text-background transition hover:opacity-85 motion-reduce:transition-none"
        to="/"
      >
        {UI_TEXT.errors.backHome}
      </Link>
    </section>
  )
}
