import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import PostListPage from './PostListPage'
import { apiFetch } from '../api/client'

vi.mock('../api/client', () => ({
  apiFetch: vi.fn(),
}))

test('renders fetched posts as links', async () => {
  apiFetch.mockResolvedValue({ results: [{ id: 1, title: 'Hello World' }] })
  render(
    <MemoryRouter>
      <PostListPage />
    </MemoryRouter>
  )
  expect(await screen.findByText('Hello World')).toBeInTheDocument()
})
