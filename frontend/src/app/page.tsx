'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useBooksQuery } from '@/hooks/use-books'
import { useMembersQuery } from '@/hooks/use-members'
import { useActiveBorrowingsQuery } from '@/hooks/use-borrowings'
import { useAuthStore } from '@/store/auth'
import apiClient from '@/lib/api-client'
import { Book, Users, RotateCw, AlertTriangle } from 'lucide-react'

export default function Dashboard() {
  const router = useRouter()
  const { isAuthenticated, loadFromStorage, isAdminOrLibrarian, isMember, updateUser, user, token } = useAuthStore()
  const [isLoading, setIsLoading] = useState(true)
  const { data: booksData } = useBooksQuery({ page_size: 1 })
  const { data: membersData } = useMembersQuery({ page_size: 1 })
  const { data: borrowingsData } = useActiveBorrowingsQuery()
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
  const docsUrl = apiBaseUrl.replace(/\/api\/v1\/?$/, '/api/docs/')

  useEffect(() => {
    // Load auth state from storage on mount only
    loadFromStorage()
    setIsLoading(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    const refreshGroups = async () => {
      if (!isAuthenticated || !user || !token) {
        return
      }
      try {
        const userResponse = await apiClient.get('/auth/user/')
        const groups = userResponse.data.user?.groups || []
        const currentGroups = user.groups || []
        const sameGroups =
          currentGroups.length === groups.length &&
          currentGroups.every((group) => groups.includes(group))

        if (!sameGroups) {
          updateUser({ ...user, groups })
        }
      } catch {
        // ignore refresh failures; keep existing state
      }
    }

    if (!isLoading) {
      refreshGroups()
    }
  }, [isLoading, isAuthenticated, user, token, updateUser])

  useEffect(() => {
    // Only redirect after loading is complete
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading || !isAuthenticated) {
    return null
  }

  const canViewMemberStats = isAdminOrLibrarian()

  // Different stats for different user roles
  const stats = canViewMemberStats ? [
    {
      label: 'Total Books',
      value: booksData?.data?.count || 0,
      icon: Book,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      label: 'Total Members',
      value: membersData?.data?.count || 0,
      icon: Users,
      color: 'bg-green-100 text-green-600',
    },
    {
      label: 'Active Borrowings',
      value: borrowingsData?.data?.count || 0,
      icon: RotateCw,
      color: 'bg-yellow-100 text-yellow-600',
    },
  ] : [
    {
      label: 'Available Books',
      value: booksData?.data?.count || 0,
      icon: Book,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      label: 'My Active Borrowings',
      value: borrowingsData?.data?.count || 0,
      icon: RotateCw,
      color: 'bg-yellow-100 text-yellow-600',
    },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to Neighborhood Library Platform</p>
      </div>

      <div className={`grid grid-cols-1 gap-6 ${canViewMemberStats ? 'md:grid-cols-3' : 'md:grid-cols-2'}`}>
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.label}
              className="bg-white rounded-lg shadow p-6 border-l-4 border-primary-600"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {isAdminOrLibrarian() && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                href="/members/new"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center font-medium"
              >
                Add New Member
              </Link>
              <Link
                href="/books/new"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center font-medium"
              >
                Add New Book
              </Link>
              <Link
                href="/borrowings/new"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center font-medium"
              >
                Record Borrowing
              </Link>
            </div>
          </div>
        )}
        {isMember() && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link
                href="/books"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center font-medium"
              >
                Browse Books
              </Link>
              <Link
                href="/borrowings"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center font-medium"
              >
                My Borrowings
              </Link>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Documentation</h2>
          <p className="text-gray-600 text-sm mb-4">
            Learn how to use the library management system by visiting our documentation.
          </p>
          <a
            href={docsUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-block px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            View Documentation
          </a>
        </div>
      </div>
    </div>
  )
}
