'use client'

import { ReactNode, useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navigation from '../components/navigation'
import ErrorBoundary from '../components/error-boundary'
import { ToastProvider } from '../components/toast-provider'
import { useAuthStore } from '../store/auth'
import './globals.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10, // 10 minutes (formerly cacheTime)
    },
  },
})

function LayoutContent({ children }: { children: ReactNode }) {
  const { loadFromStorage } = useAuthStore()

  useEffect(() => {
    // Load auth state from localStorage on app startup
    loadFromStorage()
  }, [loadFromStorage])

  return (
    <ToastProvider>
      <Navigation />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </main>
    </ToastProvider>
  )
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <QueryClientProvider client={queryClient}>
          <LayoutContent>{children}</LayoutContent>
        </QueryClientProvider>
      </body>
    </html>
  )
}
