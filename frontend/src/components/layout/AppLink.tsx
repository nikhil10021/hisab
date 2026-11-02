import type { MouseEvent, ReactNode } from 'react'

interface AppLinkProps {
  to: string
  className?: string
  children: ReactNode
}

export function AppLink({ to, className, children }: AppLinkProps) {
  function navigate(event: MouseEvent<HTMLAnchorElement>) {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) {
      return
    }

    event.preventDefault()
    window.history.pushState({}, '', to)
    window.dispatchEvent(new PopStateEvent('popstate'))
    window.scrollTo(0, 0)
  }

  return (
    <a className={className} href={to} onClick={navigate}>
      {children}
    </a>
  )
}
