import { useParams } from 'react-router-dom'
import { UI_TEXT } from '../constants/uiText'

function getCategoryTitle(slug: string | undefined): string {
  if (!slug) {
    return UI_TEXT.category.title
  }

  return slug
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function CategoryPage() {
  const { slug } = useParams()

  return (
    <section className="mx-auto max-w-3xl space-y-4">
      <h1 className="text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
        {getCategoryTitle(slug)}
      </h1>
      <p className="text-muted">{UI_TEXT.category.placeholder}</p>
    </section>
  )
}
