'use client'

import { useState } from 'react'
import { useBorrowingsQuery, useActiveBorrowingsQuery, useOverdueBorrowingsQuery } from '@/hooks/use-borrowings'
import { Plus, RotateCw, AlertTriangle } from 'lucide-react'
import Link from 'next/link'

export default function BorrowingsPage() {
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'overdue'>('active')
  const [page, setPage] = useState(1)

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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Borrowings</h1>
        <Link
          href="/borrowings/new"
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          <Plus className="w-4 h-4" />
          Record Borrowing
        </Link>
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
                      {new Date(borrowing.borrowed_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-gray-600">{borrowing.due_date}</td>
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
                      {borrowing.status === 'overdue'
                        ? `${borrowing.days_overdue} overdue`
                        : `${borrowing.days_until_due} until due`}
                    </td>
                    <td className="px-6 py-4">
                      {borrowing.status === 'active' && (
                        <Link
                          href={`/borrowings/${borrowing.id}/return`}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                        >
                          <RotateCw className="w-4 h-4" />
                        </Link>
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
