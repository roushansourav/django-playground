import { render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import App from './App'

vi.mock('./api/client', () => ({
  apiFetch: vi.fn().mockResolvedValue({ results: [] }),
}))

test('renders Blog heading', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Blog' })).toBeInTheDocument()
})
