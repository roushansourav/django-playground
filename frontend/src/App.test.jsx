import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import App from './App'

test('renders Blog heading', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Blog' })).toBeInTheDocument()
})
