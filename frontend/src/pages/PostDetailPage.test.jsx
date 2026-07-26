import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import PostDetailPage from './PostDetailPage'
import { apiFetch } from '../api/client'

vi.mock('../api/client', () => ({
  apiFetch: vi.fn(),
}))

test('renders post title, body, and tags', async () => {
  apiFetch.mockResolvedValue({
    id: 1,
    title: 'Hello',
    body: 'Body text',
    tags: ['python', 'django'],
  })
  render(
    <MemoryRouter initialEntries={['/posts/1']}>
      <Routes>
        <Route path="/posts/:id" element={<PostDetailPage />} />
      </Routes>
    </MemoryRouter>
  )
  expect(await screen.findByText('Hello')).toBeInTheDocument()
  expect(screen.getByText('Body text')).toBeInTheDocument()
  expect(screen.getByText('Tags: python, django')).toBeInTheDocument()
})
