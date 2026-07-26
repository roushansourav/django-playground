import { render, screen } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import App from './App'

vi.mock('./api/client', () => ({
  apiFetch: vi.fn().mockResolvedValue({ results: [] }),
  API_BASE_URL: 'http://127.0.0.1:8000/api',
}))

test('renders Blog nav link', () => {
  render(<App />)
  expect(screen.getByText('Blog')).toBeInTheDocument()
})

test('shows Log in link when unauthenticated', () => {
  render(<App />)
  expect(screen.getByText('Log in')).toBeInTheDocument()
})
