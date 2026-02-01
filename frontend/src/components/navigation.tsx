'use client'

import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { BookOpen, Users, RotateCw, AlertTriangle, LogOut, Menu, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import clsx from 'clsx'
import { useAuthStore } from '@/store/auth'
import apiClient from '@/lib/api-client'

export default function Navigation() {
  const pathname = usePathname()
  const router = useRouter()
  const { isAuthenticated, user, logout, loadFromStorage } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load auth state from storage on mount
    loadFromStorage()
    setLoading(false)
  }, [loadFromStorage])

  const links = [
    { href: '/', label: 'Dashboard', icon: BookOpen },
    { href: '/members', label: 'Members', icon: Users },
    { href: '/books', label: 'Books', icon: BookOpen },
    { href: '/borrowings', label: 'Borrowings', icon: RotateCw },
    { href: '/fines', label: 'Fines', icon: AlertTriangle },
  ]

  const handleLogout = async () => {
    try {
      // Call logout endpoint
      await apiClient.post('/auth/logout/')
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      // Clear local auth state
      logout()
      setMobileMenuOpen(false)
      // Redirect to login
      router.push('/login')
    }
  }

  // If not authenticated, show minimal navigation
  if (!isAuthenticated) {
    return (
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between items-center">
            <Link href="/login" className="flex items-center gap-2 font-bold text-xl text-primary-600">
              <BookOpen className="w-6 h-6" />
              Library
            </Link>
            <div className="flex gap-4">
              <Link
                href="/login"
                className="px-4 py-2 text-primary-600 font-medium hover:bg-primary-50 rounded-lg transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/signup"
                className="px-4 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>
    )
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 justify-between items-center">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary-600">
            <BookOpen className="w-6 h-6" />
            Library
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex gap-1">
            {links.map((link) => {
              const Icon = link.icon
              const isActive = pathname === link.href
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={clsx(
                    'px-3 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors',
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              )
            })}
          </div>

          {/* User Info and Logout */}
          <div className="hidden md:flex items-center gap-4">
            {user && (
              <div className="text-right pr-4 border-r border-gray-200">
                <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden pb-4 space-y-2 border-t border-gray-200 mt-4">
            {links.map((link) => {
              const Icon = link.icon
              const isActive = pathname === link.href
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={clsx(
                    'block px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 transition-colors',
                    isActive
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              )
            })}

            {user && (
              <div className="px-4 py-3 border-t border-gray-200 mt-2">
                <p className="text-sm font-medium text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
              </div>
            )}

            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        )}
      </div>
    </nav>
  )
}
