import { act, renderHook } from '@testing-library/react'
import { expect, test, vi } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'

function wrapper({ children }) {
  return <AuthProvider>{children}</AuthProvider>
}

test('login stores tokens and flips isAuthenticated', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access: 'fake-access', refresh: 'fake-refresh' }),
    })
  )
  const { result } = renderHook(() => useAuth(), { wrapper })
  expect(result.current.isAuthenticated).toBe(false)
  await act(async () => {
    await result.current.login('alice', 'testpass123')
  })
  expect(result.current.isAuthenticated).toBe(true)
  expect(localStorage.getItem('accessToken')).toBe('fake-access')
  vi.unstubAllGlobals()
})

test('login throws on invalid credentials and does not store tokens', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false }))
  const { result } = renderHook(() => useAuth(), { wrapper })
  await expect(
    act(async () => {
      await result.current.login('alice', 'wrong')
    })
  ).rejects.toThrow('Invalid username or password')
  expect(localStorage.getItem('accessToken')).toBeNull()
  vi.unstubAllGlobals()
})
