'use client'

import { useState } from 'react'
import { useBooksQuery, useDeleteBookMutation } from '@/hooks/use-books'
import { Plus, Edit, Trash2, Eye, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'
import ConfirmationDialog from '@/components/confirmation-dialog'
import { useConfirmationDialog } from '@/hooks/use-confirmation-dialog'

export default function BooksPage() {
  const { isAdminOrLibrarian } = useAuthStore()
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const { data, isLoading } = useBooksQuery({ page, search: searchQuery })
  const deleteBook = useDeleteBookMutation()
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const { dialogState, confirm, handleCancel } = useConfirmationDialog()

  const books = data?.data?.results || []

  const handleDelete = async (id: string) => {
    if (!isAdminOrLibrarian()) return
    const confirmed = await confirm({
      title: 'Delete Book',
      message: 'Are you sure you want to delete this book? This action cannot be undone.',
      confirmLabel: 'Delete',
      variant: 'danger',
    })
    if (!confirmed) return
    try {
      setDeletingId(id)
      setDeleteError(null)
      await deleteBook.mutateAsync(id)
    } catch (error: any) {
      const errorMessage = error?.response?.data?.error || 'Failed to delete book. Please try again.'
      setDeleteError(errorMessage)
    } finally {
      setDeletingId((current) => (current === id ? null : current))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Books</h1>
        {isAdminOrLibrarian() && (
          <Link
            href="/books/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            Add Book
          </Link>
        )}
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

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b border-gray-200">
          <input
            type="text"
            placeholder="Search books by title or author..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value)
              setPage(1)
            }}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Title</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Author</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Copies</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Available</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Condition</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : books.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                    No books found
                  </td>
                </tr>
              ) : (
                books.map((book) => (
                  <tr key={book.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{book.title}</td>
                    <td className="px-6 py-4 text-gray-600">{book.author}</td>
                    <td className="px-6 py-4 text-gray-600">{book.total_copies}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          book.is_available
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {book.available_copies}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600 capitalize">{book.condition}</td>
                    <td className="px-6 py-4 flex gap-2">
                      <Link
                        href={`/books/${book.id}`}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                      {isAdminOrLibrarian() && (
                        <>
                          <Link
                            href={`/books/${book.id}/edit`}
                            className="text-primary-600 hover:text-primary-700"
                          >
                            <Edit className="w-4 h-4" />
                          </Link>
                          <button
                            onClick={() => handleDelete(book.id)}
                            disabled={deletingId === book.id}
                            className="text-red-600 hover:text-red-700 disabled:opacity-50"
                            aria-label="Delete book"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </>
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
            Total: {data?.data?.count || 0} books
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={!data?.data?.previous}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={!data?.data?.next}
              className="px-3 py-1 border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <ConfirmationDialog
        isOpen={dialogState.isOpen}
        title={dialogState.title}
        message={dialogState.message}
        confirmLabel={dialogState.confirmLabel}
        cancelLabel={dialogState.cancelLabel}
        variant={dialogState.variant}
        onConfirm={dialogState.onConfirm}
        onCancel={handleCancel}
      />
    </div>
  )
}
