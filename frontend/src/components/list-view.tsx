'use client'

import { ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'

interface Column<T> {
  key: string
  label: string
  render?: (item: T) => ReactNode
  className?: string
}

interface ListViewProps<T> {
  title: string
  items: T[]
  columns: Column<T>[]
  isLoading?: boolean
  error?: string | null
  searchPlaceholder?: string
  searchQuery?: string
  onSearchChange?: (query: string) => void
  onClearError?: () => void
  actionButton?: ReactNode
  emptyMessage?: string
  getItemKey: (item: T) => string
}

export default function ListView<T>({
  title,
  items,
  columns,
  isLoading = false,
  error,
  searchPlaceholder = 'Search...',
  searchQuery = '',
  onSearchChange,
  onClearError,
  actionButton,
  emptyMessage = 'No items found',
  getItemKey,
}: ListViewProps<T>) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">{title}</h1>
        {actionButton}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
          {onClearError && (
            <button
              onClick={onClearError}
              className="text-red-600 hover:text-red-800 font-medium text-sm"
              aria-label="Close error"
            >
              ×
            </button>
          )}
        </div>
      )}

      {/* Content Card */}
      <div className="bg-white rounded-lg shadow">
        {/* Search Bar */}
        {onSearchChange && (
          <div className="p-4 border-b border-gray-200">
            <input
              type="text"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column.key}
                    className={`px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase ${column.className || ''}`}
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-4 text-center text-gray-500">
                    {emptyMessage}
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr
                    key={getItemKey(item)}
                    className="border-b border-gray-200 hover:bg-gray-50 transition-colors"
                  >
                    {columns.map((column) => (
                      <td
                        key={column.key}
                        className={`px-6 py-4 text-sm ${column.className || ''}`}
                      >
                        {column.render
                          ? column.render(item)
                          : String((item as any)[column.key] ?? '—')}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
