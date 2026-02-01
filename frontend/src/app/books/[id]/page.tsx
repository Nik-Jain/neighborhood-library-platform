'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { AlertCircle, Edit, Loader, Trash2 } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { useBookQuery, useDeleteBookMutation, useBookBorrowingHistoryQuery } from '@/hooks/use-books'
import { formatDate } from '@/lib/date'

export default function BookDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const bookId = Array.isArray(id) ? id[0] : id
  const router = useRouter()
  const { isAdminOrLibrarian } = useAuthStore()
  const bookQuery = useBookQuery(bookId)
  const deleteBook = useDeleteBookMutation()
  const [historyPage, setHistoryPage] = useState(1)
  const borrowingHistoryQuery = useBookBorrowingHistoryQuery(bookId, { page: historyPage })
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const book = bookQuery.data?.data
  const borrowingHistory = borrowingHistoryQuery.data?.data?.results || []

  const handleDelete = async () => {
    if (!isAdminOrLibrarian() || !bookId) return
    const confirmed = window.confirm('Are you sure you want to delete this book?')
    if (!confirmed) return
    try {
      setDeleteError(null)
      await deleteBook.mutateAsync(bookId)
      router.push('/books')
    } catch (error: any) {
      const errorMessage = error?.response?.data?.error || 'Failed to delete book. Please try again.'
      setDeleteError(errorMessage)
    }
  }

  if (bookQuery.isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 flex items-center gap-2 text-gray-600">
        <Loader className="w-4 h-4 animate-spin" />
        Loading book...
      </div>
    )
  }

  if (bookQuery.isError || !book) {
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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{book.title}</h1>
          <p className="text-gray-600">by {book.author}</p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/books" className="text-primary-600 hover:text-primary-700">
            Back to Books
          </Link>
          {isAdminOrLibrarian() && (
            <>
              <Link
                href={`/books/${book.id}/edit`}
                className="inline-flex items-center gap-2 px-3 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                <Edit className="w-4 h-4" />
                Edit
              </Link>
              <button
                onClick={handleDelete}
                disabled={deleteBook.isPending}
                className="inline-flex items-center gap-2 px-3 py-2 border border-red-200 text-red-700 rounded-lg hover:bg-red-50 disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </>
          )}
        </div>
      </div>

      {deleteError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-red-700 text-sm">{deleteError}</p>
          </div>
          <button
            onClick={() => setDeleteError(null)}
            className="text-red-600 hover:text-red-800 font-medium text-sm"
          >
            ×
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 overflow-hidden">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h2 className="text-sm font-semibold text-gray-500 uppercase">Book Information</h2>
            <div className="mt-3 space-y-2 text-gray-700">
              <p><span className="font-medium">ISBN:</span> {book.isbn || '—'}</p>
              <p><span className="font-medium">Publisher:</span> {book.publisher || '—'}</p>
              <p><span className="font-medium">Publication Year:</span> {book.publication_year || '—'}</p>
              <p><span className="font-medium">Language:</span> {book.language}</p>
              <p><span className="font-medium">Condition:</span> <span className="capitalize">{book.condition}</span></p>
            </div>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-gray-500 uppercase">Availability</h2>
            <div className="mt-3 space-y-2 text-gray-700">
              <p><span className="font-medium">Total Copies:</span> {book.total_copies}</p>
              <p><span className="font-medium">Available Copies:</span> {book.available_copies}</p>
              <p>
                <span className="font-medium">Status:</span>
                <span
                  className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    book.is_available
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {book.is_available ? 'Available' : 'Not Available'}
                </span>
              </p>
              <p><span className="font-medium">Total Borrowings:</span> {book.borrowing_count}</p>              <p><span className="font-medium">Active Borrowings:</span> {book.active_borrowings_count}</p>            </div>
          </div>
        </div>
        {book.description && (
          <div className="mt-6">
            <h2 className="text-sm font-semibold text-gray-500 uppercase">Description</h2>
            <p className="mt-2 text-gray-700 break-words" style={{ wordBreak: 'break-word', overflowWrap: 'break-word' }}>{book.description}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Borrowing History</h2>
          <p className="text-sm text-gray-600">Recent borrowings and returns.</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Borrowed</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Due</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Returned</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Fine</th>
              </tr>
            </thead>
            <tbody>
              {borrowingHistoryQuery.isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    Loading history...
                  </td>
                </tr>
              ) : borrowingHistory.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No borrowing history found
                  </td>
                </tr>
              ) : (
                borrowingHistory.map((borrowing) => (
                  <tr key={borrowing.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{borrowing.member_name}</td>
                    <td className="px-6 py-4 text-gray-600">
                      {formatDate(borrowing.borrowed_at)}
                    </td>
                    <td className="px-6 py-4 text-gray-600">{formatDate(borrowing.due_date)}</td>
                    <td className="px-6 py-4 text-gray-600">
                      {formatDate(borrowing.returned_at)}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${
                          borrowing.status === 'overdue'
                            ? 'bg-red-100 text-red-800'
                            : borrowing.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {borrowing.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      {borrowing.fine ? (
                        <div className="space-y-1">
                          <div>
                            <span className="font-medium">Amount:</span> ${borrowing.fine.amount}
                          </div>
                          <div>
                            <span className="font-medium">Status:</span>{' '}
                            {borrowing.fine.is_paid ? 'Paid' : 'Unpaid'}
                          </div>
                        </div>
                      ) : (
                        'No fine'
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex justify-between items-center px-6 py-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            Total: {borrowingHistoryQuery.data?.data?.count || 0} borrowings
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setHistoryPage(Math.max(1, historyPage - 1))}
              disabled={!borrowingHistoryQuery.data?.data?.previous}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setHistoryPage(historyPage + 1)}
              disabled={!borrowingHistoryQuery.data?.data?.next}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
