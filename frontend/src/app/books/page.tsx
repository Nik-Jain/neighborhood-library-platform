'use client'

import { useState } from 'react'
import { useBooksQuery, useCreateBookMutation } from '@/hooks/use-books'
import { Plus, Edit, Trash2, Eye } from 'lucide-react'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'

export default function BooksPage() {
  const { isAdminOrLibrarian } = useAuthStore()
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const { data, isLoading } = useBooksQuery({ page, search: searchQuery })

  const books = data?.data?.results || []

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
                          <button className="text-red-600 hover:text-red-700">
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
    </div>
  )
}
