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
