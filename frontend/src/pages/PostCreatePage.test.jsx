import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import PostCreatePage from './PostCreatePage'
import { apiFetch } from '../api/client'

vi.mock('../api/client', () => ({
  apiFetch: vi.fn(),
}))

test('submits the form and calls apiFetch with post data', async () => {
  apiFetch.mockResolvedValue({ id: 5, title: 'New', slug: 'new', body: 'x' })
  render(
    <MemoryRouter>
      <PostCreatePage />
    </MemoryRouter>
  )
  fireEvent.change(screen.getByLabelText('Title'), { target: { value: 'New' } })
  fireEvent.change(screen.getByLabelText('Slug'), { target: { value: 'new' } })
  fireEvent.change(screen.getByLabelText('Body'), { target: { value: 'x' } })
  fireEvent.click(screen.getByText('Create Post'))
  await waitFor(() =>
    expect(apiFetch).toHaveBeenCalledWith('/posts/', {
      method: 'POST',
      body: JSON.stringify({ title: 'New', slug: 'new', body: 'x', published: true }),
    })
  )
})
