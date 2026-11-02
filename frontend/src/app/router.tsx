import { useEffect, useState } from 'react'
import { AppLayout } from '../components/layout/AppLayout'
import { StatusPanel } from '../components/ui/StatusPanel'
import { getCalculators } from '../lib/api'
import { CalculatorPage } from '../pages/CalculatorPage'
import { HomePage } from '../pages/HomePage'
import { NotFoundPage } from '../pages/NotFoundPage'
import { customPages } from './customPages'
import type {
  AsyncState,
  CalculatorSummary,
} from '../types/calculator'

function getErrorMessage(error: unknown): string {
  return error instanceof Error
    ? error.message
    : 'Something went wrong while loading calculators.'
}

function getSlug(pathname: string): string | null {
  if (pathname === '/') {
    return null
  }

  const segment = pathname.replace(/^\/+|\/+$/g, '')

  if (!segment || segment.includes('/')) {
    return ''
  }

  try {
    return decodeURIComponent(segment)
  } catch (error) {
    if (error instanceof URIError) {
      return ''
    }

    throw error
  }
}

export function AppRouter() {
  const [pathname, setPathname] = useState(() => window.location.pathname)
  const [calculators, setCalculators] = useState<
    AsyncState<CalculatorSummary[]>
  >({ status: 'loading' })

  useEffect(() => {
    function updatePathname() {
      setPathname(window.location.pathname)
    }

    window.addEventListener('popstate', updatePathname)
    return () => window.removeEventListener('popstate', updatePathname)
  }, [])

  useEffect(() => {
    let active = true

    getCalculators()
      .then((data) => {
        if (active) {
          setCalculators({ status: 'success', data })
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setCalculators({ status: 'error', message: getErrorMessage(error) })
        }
      })

    return () => {
      active = false
    }
  }, [])

  const slug = getSlug(pathname)
  let page

  if (slug === null) {
    page = <HomePage calculators={calculators} />
  } else if (slug === '') {
    page = <NotFoundPage />
  } else if (calculators.status === 'loading') {
    page = (
      <StatusPanel
        message="Checking available pages with the backend."
        title="Loading calculators"
      />
    )
  } else if (calculators.status === 'error') {
    page = (
      <StatusPanel
        message={calculators.message}
        title="Could not load calculators"
        tone="error"
      />
    )
  } else if (calculators.status === 'success') {
    const calculator = calculators.data.find((item) => item.slug === slug)

    if (!calculator) {
      page = <NotFoundPage />
    } else {
      const CustomPage = customPages[slug] ?? CalculatorPage
      page = (
        <CustomPage
          calculator={calculator}
          key={slug}
          slug={slug}
        />
      )
    }
  } else {
    page = <NotFoundPage />
  }

  const navigationCalculators =
    calculators.status === 'success' ? calculators.data : []

  return (
    <AppLayout calculators={navigationCalculators}>
      {page}
    </AppLayout>
  )
}
