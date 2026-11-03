import { UI_TEXT } from '../constants/uiText'

export type InfoPageKey = keyof typeof UI_TEXT.pages

interface InfoPageProps {
  page: InfoPageKey
}

export function InfoPage({ page }: InfoPageProps) {
  const content = UI_TEXT.pages[page]

  return (
    <section className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {content.title}
      </h1>
      <p className="text-muted">{content.description}</p>
    </section>
  )
}
