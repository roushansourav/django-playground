import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import LoginPage from './LoginPage'
import { AuthProvider } from '../auth/AuthContext'

test('submits credentials and logs in', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access: 'fake-access', refresh: 'fake-refresh' }),
    })
  )
  render(
    <MemoryRouter>
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    </MemoryRouter>
  )
  fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'alice' } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'testpass123' } })
  fireEvent.click(screen.getByText('Log in'))
  await waitFor(() => expect(localStorage.getItem('accessToken')).toBe('fake-access'))
  vi.unstubAllGlobals()
})
