import { Link, useSearchParams } from 'react-router-dom'
import { UI_TEXT } from '../../constants/uiText'

export function Navbar() {
  const [searchParams, setSearchParams] = useSearchParams()
  const searchTerm = searchParams.get('q') ?? ''

  function updateSearchTerm(value: string) {
    const nextSearchParams = new URLSearchParams(searchParams)
    if (value) {
      nextSearchParams.set('q', value)
    } else {
      nextSearchParams.delete('q')
    }
    setSearchParams(nextSearchParams, { replace: true })
  }

  return (
    <header className="border-b border-line bg-background/90">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Link
            aria-label={UI_TEXT.navigation.home}
            className="text-xl font-bold tracking-tight text-foreground"
            to="/"
          >
            {UI_TEXT.brand.name}
            <span className="text-accent-primary">.</span>
          </Link>
          <p className="hidden text-sm text-muted xl:block">
            {UI_TEXT.brand.tagline}
          </p>
          <label className="min-w-0 flex-1 sm:max-w-md">
            <span className="sr-only">{UI_TEXT.navigation.searchLabel}</span>
            <input
              aria-label={UI_TEXT.navigation.searchLabel}
              className="min-h-11 w-full rounded-xl border border-line bg-surface px-4 text-foreground outline-none placeholder:text-muted focus:border-accent-primary"
              onChange={(event) => updateSearchTerm(event.target.value)}
              placeholder={UI_TEXT.navigation.searchPlaceholder}
              type="search"
              value={searchTerm}
            />
          </label>
          <nav aria-label={UI_TEXT.navigation.primaryNavigation}>
            <ul className="flex flex-wrap gap-4 text-sm">
              <li>
                <Link
                  className="text-muted transition-colors hover:text-foreground motion-reduce:transition-none"
                  to="/about"
                >
                  {UI_TEXT.navigation.about}
                </Link>
              </li>
              <li>
                <Link
                  className="text-muted transition-colors hover:text-foreground motion-reduce:transition-none"
                  to="/methodology"
                >
                  {UI_TEXT.navigation.methodology}
                </Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  )
}
