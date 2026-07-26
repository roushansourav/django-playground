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
