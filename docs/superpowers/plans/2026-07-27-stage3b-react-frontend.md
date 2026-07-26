# Stage 3b: React Frontend for the Blog API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. (This project has been executing plans directly in-session instead, per an explicit, previously-communicated exception for this solo learning repo — see prior stage execution history.)

**Goal:** Build a React (Vite) frontend at `frontend/` that consumes the Blog DRF API built in Stage 3a: list posts, view a post's detail (tags), log in and store a JWT, and create a post while authenticated.

**Architecture:** Plain JS (no TypeScript, per the design spec's literal "React (Vite)"). `react-router-dom` for routing, a small `apiFetch` wrapper for HTTP calls that attaches the JWT from `localStorage`, and a React Context (`AuthContext`) for auth state. Vitest + React Testing Library for TDD, matching the backend's TDD discipline. `django-cors-headers` on the backend so the Vite dev server (`localhost:5173`) can call the Django API (`127.0.0.1:8000`).

**Tech Stack:** React 18, Vite, react-router-dom, Vitest, @testing-library/react, @testing-library/jest-dom, jsdom, django-cors-headers.

## Global Constraints

- Frontend lives at `frontend/` per the design spec's directory layout (sibling to `backend/`).
- No TypeScript — plain `.jsx`/`.js`, matching the spec's minimal framing for this stage.
- Tests are TDD-first per task, same discipline as the backend: write failing test, verify failure, implement, verify pass.
- The API base URL defaults to `http://127.0.0.1:8000/api` (Stage 3a's mount point) via `import.meta.env.VITE_API_BASE_URL` with that literal as fallback — no `.env` file needed for local dev.
- No placeholders: every step below has runnable code.

---

### Task 1: CORS + Vite/React scaffold + smoke test

**Files:**
- Modify: `backend/requirements-dev.txt`
- Modify: `backend/config/settings.py`
- Create: `backend/apps/blog/tests/test_cors.py`
- Create: `frontend/` (via `npm create vite`)
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/App.test.jsx` (created this task)
- Modify: `frontend/package.json`, `frontend/vite.config.js`
- Create: `frontend/src/setupTests.js`

**Interfaces:**
- Produces: `frontend/src/App.jsx` exporting a default `App` component (a `<h1>Blog</h1>` placeholder, replaced in Task 3). `npm test` runs Vitest once (`vitest run`).

- [ ] **Step 1: Write the failing backend test**

```python
# backend/apps/blog/tests/test_cors.py
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_response_includes_cors_header(client):
    response = client.get(reverse("post-list"), HTTP_ORIGIN="http://localhost:5173")
    assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_cors.py -v`
Expected: FAIL — `KeyError: 'Access-Control-Allow-Origin'` (header absent).

- [ ] **Step 3: Install django-cors-headers**

```bash
cd ~/django-playground/backend
.venv/bin/pip install django-cors-headers
.venv/bin/pip freeze > requirements-dev.txt
```

- [ ] **Step 4: Update `backend/config/settings.py`** — add `'corsheaders'` to `INSTALLED_APPS` (after `'rest_framework'`), insert `'corsheaders.middleware.CorsMiddleware'` as the **first** entry in `MIDDLEWARE` (before `SecurityMiddleware`, per django-cors-headers' docs), and add near the `REST_FRAMEWORK` block:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/blog/tests/test_cors.py -v`
Expected: PASS.

- [ ] **Step 6: Full backend regression**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass (37 + 1 = 38).

- [ ] **Step 7: Scaffold the Vite React app**

```bash
cd ~/django-playground
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

- [ ] **Step 8: Install test tooling**

```bash
cd ~/django-playground/frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

- [ ] **Step 9: Configure Vitest** — overwrite `frontend/vite.config.js`:

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
})
```

- [ ] **Step 10: Write `frontend/src/setupTests.js`**

```js
import '@testing-library/jest-dom'
```

- [ ] **Step 11: Add a test script to `frontend/package.json`** — inside `"scripts"`, add:

```json
"test": "vitest run"
```

- [ ] **Step 12: Write the failing frontend test**

```jsx
// frontend/src/App.test.jsx
import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import App from './App'

test('renders Blog heading', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: 'Blog' })).toBeInTheDocument()
})
```

- [ ] **Step 13: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — the scaffolded `App.jsx` renders Vite/React boilerplate, not a "Blog" heading.

- [ ] **Step 14: Replace `frontend/src/App.jsx`**

```jsx
function App() {
  return (
    <div>
      <h1>Blog</h1>
    </div>
  )
}

export default App
```

- [ ] **Step 15: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS.

- [ ] **Step 16: Commit**

```bash
cd ~/django-playground
git add backend/requirements-dev.txt backend/config/settings.py backend/apps/blog/tests/test_cors.py frontend/
git commit -m "Add CORS support and scaffold React frontend with Vitest"
```

---

### Task 2: API client + Post list page

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/api/client.test.js`
- Create: `frontend/src/pages/PostListPage.jsx`
- Create: `frontend/src/pages/PostListPage.test.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/App.test.jsx`
- Modify: `frontend/package.json` (add `react-router-dom`)

**Interfaces:**
- Consumes: none new from Task 1 beyond the scaffold.
- Produces: `apiFetch(path, options)` (`frontend/src/api/client.js`) — resolves to parsed JSON on 2xx, throws `Error(detail-or-status-message)` otherwise, attaches `Authorization: Bearer <token>` when `localStorage.getItem('accessToken')` is set. `PostListPage` (default export) — fetches `/posts/` on mount, renders each post title as a `Link` to `/posts/:id`.

- [ ] **Step 1: Install react-router-dom**

```bash
cd ~/django-playground/frontend
npm install react-router-dom
```

- [ ] **Step 2: Write the failing tests for the API client**

```js
// frontend/src/api/client.test.js
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./client"` (file doesn't exist).

- [ ] **Step 4: Write `frontend/src/api/client.js`**

```js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

function getAccessToken() {
  return localStorage.getItem('accessToken')
}

export async function apiFetch(path, options = {}) {
  const token = getAccessToken()
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }
  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed with status ${response.status}`)
  }
  if (response.status === 204) {
    return null
  }
  return response.json()
}

export { API_BASE_URL, getAccessToken }
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS for the 3 client tests (App.test.jsx will fail here — that's expected, fixed in Step 10).

- [ ] **Step 6: Write the failing test for PostListPage**

```jsx
// frontend/src/pages/PostListPage.test.jsx
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
```

- [ ] **Step 7: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./PostListPage"`.

- [ ] **Step 8: Write `frontend/src/pages/PostListPage.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api/client'

function PostListPage() {
  const [posts, setPosts] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    apiFetch('/posts/')
      .then((data) => setPosts(data.results))
      .catch((err) => setError(err.message))
  }, [])

  if (error) {
    return <p>Error: {error}</p>
  }

  return (
    <ul>
      {posts.map((post) => (
        <li key={post.id}>
          <Link to={`/posts/${post.id}`}>{post.title}</Link>
        </li>
      ))}
    </ul>
  )
}

export default PostListPage
```

- [ ] **Step 9: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS for PostListPage (App.test.jsx still failing — fixed next).

- [ ] **Step 10: Wire `PostListPage` into `App.jsx` and update its test**

```jsx
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import PostListPage from './pages/PostListPage'

function App() {
  return (
    <BrowserRouter>
      <h1>Blog</h1>
      <Routes>
        <Route path="/" element={<PostListPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

```jsx
// frontend/src/App.test.jsx
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
```

- [ ] **Step 11: Full frontend regression**

Run: `cd ~/django-playground/frontend && npm test`
Expected: all pass (App, client x3, PostListPage = 5 tests).

- [ ] **Step 12: Commit**

```bash
cd ~/django-playground
git add frontend/
git commit -m "Add API client and Post list page"
```

---

### Task 3: Auth — login page, AuthContext, nav

**Files:**
- Create: `frontend/src/auth/AuthContext.jsx`
- Create: `frontend/src/auth/AuthContext.test.jsx`
- Create: `frontend/src/pages/LoginPage.jsx`
- Create: `frontend/src/pages/LoginPage.test.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/App.test.jsx`
- Modify: `frontend/src/setupTests.js` (clear `localStorage` between tests)

**Interfaces:**
- Consumes: `API_BASE_URL` (Task 2's `api/client.js`).
- Produces: `AuthProvider` (wraps the app, no props besides `children`) and `useAuth()` (`frontend/src/auth/AuthContext.jsx`) returning `{ accessToken, isAuthenticated, login(username, password), logout() }`. `login` POSTs to `${API_BASE_URL}/token/`, stores `accessToken`/`refreshToken` in `localStorage` on success, throws on failure. `LoginPage` (default export) — a form calling `login` and navigating to `/` on success.

- [ ] **Step 1: Ensure test isolation** — append to `frontend/src/setupTests.js`:

```js
import { afterEach } from 'vitest'

afterEach(() => {
  localStorage.clear()
})
```

- [ ] **Step 2: Write the failing test for AuthContext**

```jsx
// frontend/src/auth/AuthContext.test.jsx
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./AuthContext"`.

- [ ] **Step 4: Write `frontend/src/auth/AuthContext.jsx`**

```jsx
import { createContext, useContext, useState } from 'react'
import { API_BASE_URL } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => localStorage.getItem('accessToken'))

  async function login(username, password) {
    const response = await fetch(`${API_BASE_URL}/token/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!response.ok) {
      throw new Error('Invalid username or password')
    }
    const data = await response.json()
    localStorage.setItem('accessToken', data.access)
    localStorage.setItem('refreshToken', data.refresh)
    setAccessToken(data.access)
  }

  function logout() {
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    setAccessToken(null)
  }

  return (
    <AuthContext.Provider value={{ accessToken, isAuthenticated: !!accessToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS for both AuthContext tests.

- [ ] **Step 6: Write the failing test for LoginPage**

```jsx
// frontend/src/pages/LoginPage.test.jsx
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
```

- [ ] **Step 7: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./LoginPage"`.

- [ ] **Step 8: Write `frontend/src/pages/LoginPage.jsx`**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p role="alert">{error}</p>}
      <label htmlFor="username">Username</label>
      <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button type="submit">Log in</button>
    </form>
  )
}

export default LoginPage
```

- [ ] **Step 9: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS.

- [ ] **Step 10: Wire auth into `App.jsx` and update its test**

```jsx
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import PostListPage from './pages/PostListPage'
import LoginPage from './pages/LoginPage'

function Nav() {
  const { isAuthenticated, logout } = useAuth()
  return (
    <nav>
      <Link to="/">Blog</Link>
      {isAuthenticated ? (
        <button onClick={logout}>Log out</button>
      ) : (
        <Link to="/login">Log in</Link>
      )}
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<PostListPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
```

```jsx
// frontend/src/App.test.jsx
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
```

- [ ] **Step 11: Full frontend regression**

Run: `cd ~/django-playground/frontend && npm test`
Expected: all pass.

- [ ] **Step 12: Commit**

```bash
cd ~/django-playground
git add frontend/
git commit -m "Add login page, AuthContext, and auth-aware nav"
```

---

### Task 4: Post detail page + create post form

**Files:**
- Create: `frontend/src/pages/PostDetailPage.jsx`
- Create: `frontend/src/pages/PostDetailPage.test.jsx`
- Create: `frontend/src/pages/PostCreatePage.jsx`
- Create: `frontend/src/pages/PostCreatePage.test.jsx`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/App.test.jsx`

**Interfaces:**
- Consumes: `apiFetch` (Task 2), `useAuth` (Task 3).
- Produces: `PostDetailPage` (default export) — reads `id` from the route, fetches `/posts/:id/`, renders title/body/tags. `PostCreatePage` (default export) — a form that POSTs to `/posts/` via `apiFetch` and navigates to the new post's detail page on success.

- [ ] **Step 1: Write the failing test for PostDetailPage**

```jsx
// frontend/src/pages/PostDetailPage.test.jsx
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./PostDetailPage"`.

- [ ] **Step 3: Write `frontend/src/pages/PostDetailPage.jsx`**

```jsx
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiFetch } from '../api/client'

function PostDetailPage() {
  const { id } = useParams()
  const [post, setPost] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiFetch(`/posts/${id}/`)
      .then(setPost)
      .catch((err) => setError(err.message))
  }, [id])

  if (error) {
    return <p>Error: {error}</p>
  }
  if (!post) {
    return <p>Loading...</p>
  }

  return (
    <article>
      <h2>{post.title}</h2>
      <p>{post.body}</p>
      <p>Tags: {post.tags.length > 0 ? post.tags.join(', ') : 'none'}</p>
    </article>
  )
}

export default PostDetailPage
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS.

- [ ] **Step 5: Write the failing test for PostCreatePage**

```jsx
// frontend/src/pages/PostCreatePage.test.jsx
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
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd ~/django-playground/frontend && npm test`
Expected: FAIL — `Failed to resolve import "./PostCreatePage"`.

- [ ] **Step 7: Write `frontend/src/pages/PostCreatePage.jsx`**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'

function PostCreatePage() {
  const [title, setTitle] = useState('')
  const [slug, setSlug] = useState('')
  const [body, setBody] = useState('')
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function handleSubmit(event) {
    event.preventDefault()
    try {
      const post = await apiFetch('/posts/', {
        method: 'POST',
        body: JSON.stringify({ title, slug, body, published: true }),
      })
      navigate(`/posts/${post.id}`)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {error && <p role="alert">{error}</p>}
      <label htmlFor="title">Title</label>
      <input id="title" value={title} onChange={(e) => setTitle(e.target.value)} />
      <label htmlFor="slug">Slug</label>
      <input id="slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
      <label htmlFor="body">Body</label>
      <textarea id="body" value={body} onChange={(e) => setBody(e.target.value)} />
      <button type="submit">Create Post</button>
    </form>
  )
}

export default PostCreatePage
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd ~/django-playground/frontend && npm test`
Expected: PASS.

- [ ] **Step 9: Wire both pages into `App.jsx` and update its test**

```jsx
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth/AuthContext'
import PostListPage from './pages/PostListPage'
import PostDetailPage from './pages/PostDetailPage'
import PostCreatePage from './pages/PostCreatePage'
import LoginPage from './pages/LoginPage'

function Nav() {
  const { isAuthenticated, logout } = useAuth()
  return (
    <nav>
      <Link to="/">Blog</Link>
      {isAuthenticated ? (
        <>
          <Link to="/posts/new">New Post</Link>
          <button onClick={logout}>Log out</button>
        </>
      ) : (
        <Link to="/login">Log in</Link>
      )}
    </nav>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Nav />
        <Routes>
          <Route path="/" element={<PostListPage />} />
          <Route path="/posts/new" element={<PostCreatePage />} />
          <Route path="/posts/:id" element={<PostDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
```

```jsx
// frontend/src/App.test.jsx
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

test('shows New Post link when authenticated', () => {
  localStorage.setItem('accessToken', 'fake-token')
  render(<App />)
  expect(screen.getByText('New Post')).toBeInTheDocument()
})
```

- [ ] **Step 10: Full frontend regression**

Run: `cd ~/django-playground/frontend && npm test`
Expected: all pass.

- [ ] **Step 11: Full backend regression (unaffected, sanity check)**

Run: `cd ~/django-playground/backend && .venv/bin/python -m pytest apps/ -v`
Expected: all pass (38).

- [ ] **Step 12: Commit**

```bash
cd ~/django-playground
git add frontend/
git commit -m "Add Post detail page and Create Post form"
```

---

## After this plan

The frontend can list posts, view a post's detail with tags, log in against the JWT endpoint, and create a post while authenticated — a complete, portfolio-demoable loop against the Stage 3a API. Manual end-to-end verification: run `python manage.py runserver` (backend, port 8000) and `npm run dev` (frontend, port 5173) side by side, and click through signup → login → create post → view in list → view detail.
