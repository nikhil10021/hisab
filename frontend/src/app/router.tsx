import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppLayout } from '../components/layout/AppLayout'
import { CalculatorPage } from '../pages/CalculatorPage'
import { CategoryPage } from '../pages/CategoryPage'
import { HomePage } from '../pages/HomePage'
import { InfoPage } from '../pages/InfoPage'
import { NotFoundPage } from '../pages/NotFoundPage'

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route element={<HomePage />} index />
          <Route element={<CalculatorPage />} path="calculators/:slug" />
          <Route element={<CategoryPage />} path="category/:slug" />
          <Route element={<InfoPage page="about" />} path="about" />
          <Route element={<InfoPage page="methodology" />} path="methodology" />
          <Route element={<InfoPage page="terms" />} path="terms" />
          <Route element={<InfoPage page="privacy" />} path="privacy" />
          <Route element={<NotFoundPage />} path="*" />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
