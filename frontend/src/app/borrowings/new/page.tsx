'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { AlertCircle, Loader } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { useMembersQuery } from '@/hooks/use-members'
import { useBooksQuery } from '@/hooks/use-books'
import { useCreateBorrowingMutation } from '@/hooks/use-borrowings'

export default function NewBorrowingPage() {
  const router = useRouter()
  const { isAdminOrLibrarian } = useAuthStore()
  const createBorrowing = useCreateBorrowingMutation()

  const membersQuery = useMembersQuery({ page: 1, page_size: 100 })
  const booksQuery = useBooksQuery({ page: 1, page_size: 100, is_available: true })

  const members = membersQuery.data?.data?.results || []
  const books = booksQuery.data?.data?.results || []

  const [formData, setFormData] = useState({
    member_id: '',
    book_id: '',
    due_date: '',
    notes: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [generalError, setGeneralError] = useState('')

  if (!isAdminOrLibrarian()) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold text-gray-900">Access denied</h1>
        <p className="text-gray-600 mt-2">Only admins or librarians can record borrowings.</p>
        <Link href="/borrowings" className="text-primary-600 hover:text-primary-700 mt-4 inline-block">
          Back to Borrowings
        </Link>
      </div>
    )
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const nextErrors: Record<string, string> = {}
    if (!formData.member_id) nextErrors.member_id = 'Member is required'
    if (!formData.book_id) nextErrors.book_id = 'Book is required'
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setGeneralError('')

    if (!validate()) return

    try {
      const payload: any = {
        member_id: formData.member_id,
        book_id: formData.book_id,
      }
      if (formData.due_date) payload.due_date = formData.due_date
      if (formData.notes.trim()) payload.notes = formData.notes.trim()

      await createBorrowing.mutateAsync(payload)
      router.push('/borrowings')
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
        setGeneralError('Failed to create borrowing. Please try again.')
      }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Record Borrowing</h1>
        <Link href="/borrowings" className="text-primary-600 hover:text-primary-700">
          Back to Borrowings
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        {generalError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3 mb-6">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
            <p className="text-red-700 text-sm">{generalError}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Member *</label>
            <select
              name="member_id"
              value={formData.member_id}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg ${errors.member_id ? 'border-red-500' : 'border-gray-300'}`}
              required
            >
              <option value="">Select a member</option>
              {members.map((member: any) => (
                <option key={member.id} value={member.id}>
                  {member.full_name} ({member.email})
                </option>
              ))}
            </select>
            {errors.member_id && <p className="text-red-600 text-xs mt-1">{errors.member_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Book *</label>
            <select
              name="book_id"
              value={formData.book_id}
              onChange={handleChange}
              className={`w-full px-4 py-2 border rounded-lg ${errors.book_id ? 'border-red-500' : 'border-gray-300'}`}
              required
            >
              <option value="">Select a book</option>
              {books.map((book: any) => (
                <option key={book.id} value={book.id}>
                  {book.title} — {book.author}
                </option>
              ))}
            </select>
            {errors.book_id && <p className="text-red-600 text-xs mt-1">{errors.book_id}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Due Date (optional)</label>
            <input
              name="due_date"
              type="date"
              value={formData.due_date}
              onChange={handleChange}
              className="w-full px-4 py-2 border rounded-lg border-gray-300"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-4 py-2 border rounded-lg border-gray-300"
            />
          </div>

          <button
            type="submit"
            disabled={createBorrowing.isPending}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2 disabled:opacity-50"
          >
            {createBorrowing.isPending && <Loader className="w-4 h-4 animate-spin" />}
            Record Borrowing
          </button>
        </form>
      </div>
    </div>
  )
}
