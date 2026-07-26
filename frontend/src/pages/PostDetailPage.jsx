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
