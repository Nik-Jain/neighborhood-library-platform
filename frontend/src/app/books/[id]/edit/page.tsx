'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'
import { AlertCircle, Loader } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { useBookQuery, useUpdateBookMutation } from '@/hooks/use-books'

export default function EditBookPage() {
  const { id } = useParams<{ id: string }>()
  const bookId = Array.isArray(id) ? id[0] : id
  const router = useRouter()
  const { isAdminOrLibrarian } = useAuthStore()
  const bookQuery = useBookQuery(bookId)
  const updateBook = useUpdateBookMutation()

  const [formData, setFormData] = useState({
    isbn: '',
    title: '',
    author: '',
    publisher: '',
    publication_year: '',
    description: '',
    total_copies: 1,
    available_copies: 1,
    condition: 'excellent',
    language: 'English',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState('')

  useEffect(() => {
    if (bookQuery.data?.data) {
      const book = bookQuery.data.data
      setFormData({
        isbn: book.isbn || '',
        title: book.title || '',
        author: book.author || '',
        publisher: book.publisher || '',
        publication_year: book.publication_year?.toString() || '',
        description: book.description || '',
        total_copies: book.total_copies || 1,
        available_copies: book.available_copies || 1,
        condition: book.condition || 'excellent',
        language: book.language || 'English',
      })
    }
  }, [bookQuery.data])

  if (!isAdminOrLibrarian()) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Access denied</h1>
        <p className="text-gray-600 mt-2">Only admins or librarians can edit books.</p>
        <Link href="/books" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Back to Books
        </Link>
      </div>
    )
  }

  if (bookQuery.isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 flex items-center gap-2 text-gray-600">
        <Loader className="w-4 h-4 animate-spin" />
        Loading book...
      </div>
    )
  }

  if (bookQuery.isError || !bookQuery.data?.data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-start gap-3 text-red-700">
          <AlertCircle className="w-5 h-5 mt-0.5" />
          <div>
            <h1 className="text-lg font-semibold">Unable to load book</h1>
            <p className="text-sm text-red-600 mt-1">Please try again.</p>
          </div>
        </div>
        <Link href="/books" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Back to Books
        </Link>
      </div>
    )
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? (value === '' ? '' : Number(value)) : value,
    }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const nextErrors: Record<string, string> = {}
    if (!formData.title.trim()) nextErrors.title = 'Title is required'
    if (!formData.author.trim()) nextErrors.author = 'Author is required'
    if (formData.total_copies < 1) nextErrors.total_copies = 'Total copies must be at least 1'
    if (formData.available_copies < 0) nextErrors.available_copies = 'Available copies cannot be negative'
    if (formData.available_copies > formData.total_copies) {
      nextErrors.available_copies = 'Available copies cannot exceed total copies'
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setGeneralError('')

    if (!validate() || !bookId) return

    try {
      const payload: any = {
        title: formData.title.trim(),
        author: formData.author.trim(),
        total_copies: formData.total_copies,
        available_copies: formData.available_copies,
        condition: formData.condition,
        language: formData.language,
      }
      
      // Include optional fields explicitly
      if (formData.isbn.trim()) {
        payload.isbn = formData.isbn.trim()
      } else {
        payload.isbn = null
      }
      
      if (formData.publisher.trim()) {
        payload.publisher = formData.publisher.trim()
      } else {
        payload.publisher = null
      }
      
      if (formData.publication_year) {
        payload.publication_year = Number(formData.publication_year)
      } else {
        payload.publication_year = null
      }
      
      // Always include description field
      if (formData.description.trim()) {
        payload.description = formData.description.trim()
      } else {
        payload.description = null
      }
      
      await updateBook.mutateAsync({
        id: bookId,
        data: payload,
      })
      router.push(`/books/${bookId}`)
    } catch (err: any) {
      const data = err?.response?.data
      if (data && typeof data === 'object') {
        const nextErrors: Record<string, string> = {}
        Object.keys(data).forEach((key) => {
          const messages = Array.isArray(data[key]) ? data[key] : [data[key]]
          nextErrors[key] = messages.join(', ')
        })
        setErrors(nextErrors)
      } else {
        setGeneralError('Failed to update book. Please try again.')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Edit Book</h1>
        <div className="flex items-center gap-3">
          <Link href={`/books/${bookId}`} className="text-primary-600 hover:text-primary-700">
            Back to Book
          </Link>
          <Link href="/books" className="text-gray-600 hover:text-gray-800">
            Books List
          </Link>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {generalError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 mb-6">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <p className="text-red-700 text-sm">{generalError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
              <input
                name="title"
                value={formData.title}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.title ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.title && <p className="text-red-600 text-xs mt-1">{errors.title}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Author *</label>
              <input
                name="author"
                value={formData.author}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.author ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.author && <p className="text-red-600 text-xs mt-1">{errors.author}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">ISBN</label>
              <input
                name="isbn"
                value={formData.isbn}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Publisher</label>
              <input
                name="publisher"
                value={formData.publisher}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Publication Year</label>
              <input
                name="publication_year"
                type="number"
                min="1000"
                max="2100"
                value={formData.publication_year}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
              <input
                name="language"
                value={formData.language}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={4}
              className="w-full px-4 py-2 border rounded-lg border-gray-300"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Total Copies *</label>
              <input
                name="total_copies"
                type="number"
                min="1"
                value={formData.total_copies}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.total_copies ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.total_copies && <p className="text-red-600 text-xs mt-1">{errors.total_copies}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Available Copies *</label>
              <input
                name="available_copies"
                type="number"
                min="0"
                value={formData.available_copies}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg ${errors.available_copies ? 'border-red-500' : 'border-gray-300'}`}
                required
              />
              {errors.available_copies && <p className="text-red-600 text-xs mt-1">{errors.available_copies}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Condition</label>
              <select
                name="condition"
                value={formData.condition}
                onChange={handleChange}
                className="w-full px-4 py-2 border rounded-lg border-gray-300"
              >
                <option value="excellent">Excellent</option>
                <option value="good">Good</option>
                <option value="fair">Fair</option>
                <option value="poor">Poor</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={updateBook.isPending}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2 disabled:opacity-50"
          >
            {updateBook.isPending && <Loader className="w-4 h-4 animate-spin" />}
            Save Changes
          </button>
        </form>
      </div>
    </div>
  )
}
