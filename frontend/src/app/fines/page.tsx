'use client'

import { useState } from 'react'
import { useFinesQuery, useUnpaidFinesQuery, useMarkAsPaidMutation } from '@/hooks/use-fines'
import { AlertTriangle, CheckCircle } from 'lucide-react'
import { formatDate } from '@/lib/date'

export default function FinesPage() {
  const [showUnpaidOnly, setShowUnpaidOnly] = useState(true)
  const [page, setPage] = useState(1)
  const [markingAsPaidId, setMarkingAsPaidId] = useState<string | null>(null)

  const query = showUnpaidOnly ? useUnpaidFinesQuery({ page }) : useFinesQuery({ page })
  const { data, isLoading } = query
  const markAsPaidMutation = useMarkAsPaidMutation()

  const fines = data?.data?.results || []
  const totalAmount = fines.reduce((sum, fine) => sum + parseFloat(fine.amount), 0)

  const handleMarkAsPaid = async (fineId: string) => {
    const confirmed = window.confirm('Mark this fine as paid?')
    if (!confirmed) return
    try {
      setMarkingAsPaidId(fineId)
      await markAsPaidMutation.mutateAsync(fineId)
    } catch (error) {
      console.error('Failed to mark fine as paid:', error)
      alert('Failed to mark fine as paid. Please try again.')
    } finally {
      setMarkingAsPaidId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Fines</h1>
        <button
          onClick={() => {
            setShowUnpaidOnly(!showUnpaidOnly)
            setPage(1)
          }}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            showUnpaidOnly
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          {showUnpaidOnly ? 'Show All' : 'Show Unpaid Only'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm font-medium">
                {showUnpaidOnly ? 'Total Fines (Unpaid)' : 'Total Fines'}
              </p>
              <p className="text-3xl font-bold text-gray-900 mt-2">${totalAmount.toFixed(2)}</p>
            </div>
            <AlertTriangle className="w-12 h-12 text-red-600" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm font-medium">Fine Records</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{data?.data?.count || 0}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Member</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Book</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Reason</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase">Date</th>
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
              ) : fines.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    No fines found
                  </td>
                </tr>
              ) : (
                fines.map((fine) => (
                  <tr key={fine.id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">{fine.member_name || '-'}</td>
                    <td className="px-6 py-4 text-gray-600">{fine.book_title || '-'}</td>
                    <td className="px-6 py-4 font-medium text-gray-900">${parseFloat(fine.amount).toFixed(2)}</td>
                    <td className="px-6 py-4 text-gray-600">{fine.reason}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          fine.is_paid
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {fine.is_paid ? 'Paid' : 'Unpaid'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      {formatDate(fine.created_at)}
                    </td>
                    <td className="px-6 py-4">
                      {!fine.is_paid && (
                        <button
                          onClick={() => handleMarkAsPaid(fine.id)}
                          disabled={markingAsPaidId === fine.id}
                          className="text-green-600 hover:text-green-700 disabled:opacity-50"
                          aria-label="Mark as paid"
                          title="Mark as paid"
                        >
                          <CheckCircle className="w-5 h-5" />
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
            Total: {data?.data?.count || 0} fines
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
