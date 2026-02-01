'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuthStore } from '@/store/auth'
import apiClient from '@/lib/api-client'
import { BookOpen, AlertCircle, Loader } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Clear any existing auth state first to prevent permission leaks
      if (typeof window !== 'undefined') {
        localStorage.removeItem('authToken')
        localStorage.removeItem('user')
      }

      const response = await apiClient.post('/auth/login/', {
        email,
        password,
      })

      const { token, member } = response.data

      // Fetch user info with groups using the NEW token
      try {
        const userResponse = await apiClient.get('/auth/user/', {
          headers: { Authorization: `Token ${token}` }
        })
        
        const userWithGroups = {
          ...member,
          groups: userResponse.data.user?.groups || [],
        }
        
        // Store auth data with groups
        setAuth(userWithGroups, token)
      } catch (userErr) {
        // Fallback if /auth/user/ fails
        setAuth(member, token)
      }

      // Redirect to dashboard
      router.push('/')
    } catch (err: any) {
      const errorMessage = err.response?.data?.password?.[0] || 
                          err.response?.data?.error || 
                          'Login failed. Please try again.'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 p-4">
      <div className="w-full max-w-md">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <BookOpen className="w-8 h-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Library</h1>
          </div>
          <h2 className="text-xl font-semibold text-gray-700">
            Neighborhood Library Platform
          </h2>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 space-y-6">
          <div>
            <h3 className="text-2xl font-bold text-gray-900">Sign In</h3>
            <p className="text-gray-600 text-sm mt-1">
              Enter your email and password to access your account
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-red-800 text-sm font-medium">Login Error</p>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading && <Loader className="w-4 h-4 animate-spin" />}
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">New member?</span>
            </div>
          </div>

          {/* Signup Link */}
          <Link
            href="/signup"
            className="w-full border-2 border-primary-600 text-primary-600 py-2 rounded-lg hover:bg-primary-50 transition-colors font-medium text-center"
          >
            Create Account
          </Link>

        </div>

        {/* Footer */}
        <p className="text-center text-gray-600 text-sm mt-6">
          © 2026 Neighborhood Library Platform. All rights reserved.
        </p>
      </div>
    </div>
  )
}
