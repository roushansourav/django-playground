import { afterEach, expect, test, vi } from 'vitest'
import { apiFetch } from './client'

afterEach(() => {
  localStorage.clear()
  vi.unstubAllGlobals()
})

test('returns parsed JSON on success', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ id: 1 }),
    })
  )
  const data = await apiFetch('/posts/')
  expect(data).toEqual({ id: 1 })
})

test('attaches Authorization header when an access token is stored', async () => {
  localStorage.setItem('accessToken', 'abc123')
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: () => Promise.resolve({}),
  })
  vi.stubGlobal('fetch', fetchMock)
  await apiFetch('/posts/')
  expect(fetchMock.mock.calls[0][1].headers.Authorization).toBe('Bearer abc123')
})

test('throws on a non-ok response', async () => {
  vi.stubGlobal(
    'fetch',
    vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: () => Promise.resolve({ detail: 'Forbidden' }),
    })
  )
  await expect(apiFetch('/posts/')).rejects.toThrow('Forbidden')
})
