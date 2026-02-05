'use client'

import { Component, ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">
                Something went wrong
              </h1>
            </div>
            
            <p className="text-gray-600 mb-4">
              We're sorry, but something unexpected happened. Please try refreshing the page.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                  Error details
                </summary>
                <pre className="mt-2 text-xs bg-gray-100 p-3 rounded overflow-auto max-h-40">
                  {this.state.error.toString()}
                  {this.state.error.stack}
                </pre>
              </details>
            )}

            <button
              onClick={() => window.location.reload()}
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              Refresh page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
