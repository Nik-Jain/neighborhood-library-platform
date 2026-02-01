'use client'

import { useState } from 'react'
import { useBorrowingsQuery, useActiveBorrowingsQuery, useOverdueBorrowingsQuery, useReturnBookMutation } from '@/hooks/use-borrowings'
import { Plus, RotateCw, AlertTriangle, AlertCircle } from 'lucide-react'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'
import { formatDate } from '@/lib/date'

export default function BorrowingsPage() {
  const { isAdminOrLibrarian } = useAuthStore()
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'overdue'>('active')
  const [page, setPage] = useState(1)
  const returnBook = useReturnBookMutation()
  const [returningId, setReturningId] = useState<string | null>(null)
  const [returnError, setReturnError] = useState<string | null>(null)
  const [returnSuccess, setReturnSuccess] = useState<string | null>(null)

  let query
  if (filterStatus === 'active') {
    query = useActiveBorrowingsQuery({ page })
  } else if (filterStatus === 'overdue') {
    query = useOverdueBorrowingsQuery({ page })
  } else {
    query = useBorrowingsQuery({ page })
  }

  const { data, isLoading } = query
  const borrowings = data?.data?.results || []

  const handleReturn = async (id: string, bookTitle: string) => {
    if (!isAdminOrLibrarian()) return
    const confirmed = window.confirm(`Are you sure you want to mark "${bookTitle}" as returned?`)
    if (!confirmed) return
    try {
      setReturningId(id)
      setReturnError(null)
      setReturnSuccess(null)
      const response = await returnBook.mutateAsync(id)
      const fineAmount = response?.data?.fine?.amount
      if (fineAmount) {
        setReturnSuccess(`Book "${bookTitle}" returned. Fine created: $${fineAmount}.`)
      } else {
        setReturnSuccess(`Book "${bookTitle}" has been marked as returned successfully.`)
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.error || 'Failed to return book. Please try again.'
      setReturnError(errorMessage)
    } finally {
      setReturningId((current) => (current === id ? null : current))
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">{isAdminOrLibrarian() ? 'Borrowings' : 'My Borrowings'}</h1>
        {isAdminOrLibrarian() && (
          <Link
            href="/borrowings/new"
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
            <Plus className="w-4 h-4" />
            Record Borrowing
          </Link>
        )}
      </div>

      <div className="flex gap-2">
        {['all', 'active', 'overdue'].map((status) => (
          <button
            key={status}
            onClick={() => {
              setFilterStatus(status as any)
              setPage(1)
            }}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              filterStatus === status
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {returnError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-red-700 text-sm">{returnError}</p>
          </div>
          <button
            onClick={() => setReturnError(null)}
            className="text-red-600 hover:text-red-800 font-medium text-sm"
          >
            ×
          </button>
        </div>
      )}

      {returnSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-green-700 text-sm">{returnSuccess}</p>
          </div>
          <button
            onClick={() => setReturnSuccess(null)}
            className="text-green-600 hover:text-green-800 font-medium text-sm"
          >
            ×
          </button>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Book</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Borrowed</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Days</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : borrowings.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    No borrowings found
                  </td>
                </tr>
              ) : (
                borrowings.map((borrowing) => (
                  <tr key={borrowing.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{borrowing.member_name}</td>
                    <td className="px-6 py-4 text-gray-600">{borrowing.book_title}</td>
                    <td className="px-6 py-4 text-gray-600">
                      {formatDate(borrowing.borrowed_at)}
                    </td>
                    <td className="px-6 py-4 text-gray-600">{formatDate(borrowing.due_date)}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 w-fit ${
                          borrowing.status === 'overdue'
                            ? 'bg-red-100 text-red-800'
                            : borrowing.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {borrowing.status === 'overdue' && <AlertTriangle className="w-3 h-3" />}
                        {borrowing.status.charAt(0).toUpperCase() + borrowing.status.slice(1)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {borrowing.status === 'returned'
                        ? '—'
                        : borrowing.status === 'overdue'
                        ? `${borrowing.days_overdue} overdue`
                        : `${borrowing.days_until_due} until due`}
                    </td>
                    <td className="px-6 py-4">
                      {(borrowing.status === 'active' || borrowing.status === 'overdue') && isAdminOrLibrarian() && (
                        <button
                          onClick={() => handleReturn(borrowing.id, borrowing.book_title)}
                          disabled={returningId === borrowing.id}
                          className="text-primary-600 hover:text-primary-700 disabled:opacity-50"
                          title="Mark as returned"
                        >
                          <RotateCw className={`w-4 h-4 ${returningId === borrowing.id ? 'animate-spin' : ''}`} />
                        </button>
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
            Total: {data?.data?.count || 0} borrowings
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
