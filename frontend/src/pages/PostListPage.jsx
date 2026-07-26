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
