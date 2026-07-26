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
