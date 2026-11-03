import { Link } from 'react-router-dom'
import { UI_TEXT } from '../../constants/uiText'

export function Footer() {
  return (
    <footer className="border-t border-line">
      <nav
        aria-label={UI_TEXT.navigation.footerNavigation}
        className="mx-auto flex max-w-7xl flex-wrap gap-x-6 gap-y-3 px-4 py-6 text-sm sm:px-6 lg:px-8"
      >
        <Link className="text-muted hover:text-foreground" to="/about">
          {UI_TEXT.navigation.about}
        </Link>
        <Link className="text-muted hover:text-foreground" to="/methodology">
          {UI_TEXT.navigation.methodology}
        </Link>
        <Link className="text-muted hover:text-foreground" to="/terms">
          {UI_TEXT.navigation.terms}
        </Link>
        <Link className="text-muted hover:text-foreground" to="/privacy">
          {UI_TEXT.navigation.privacy}
        </Link>
      </nav>
    </footer>
  )
}
