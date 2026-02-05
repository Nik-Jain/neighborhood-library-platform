/**
 * Global error handler hook
 * Provides consistent error handling and user feedback across the application
 */

import { useToast } from '@/components/toast-provider'
import { useCallback } from 'react'

interface ErrorResponse {
  response?: {
    data?: {
      error?: string
      detail?: string
      message?: string
    }
    status?: number
  }
  message?: string
}

export function useErrorHandler() {
  const toast = useToast()

  const handleError = useCallback(
    (error: ErrorResponse | unknown, defaultMessage = 'An error occurred. Please try again.') => {
      let errorMessage = defaultMessage

      if (error && typeof error === 'object' && 'response' in error) {
        const err = error as ErrorResponse
        errorMessage = 
          err.response?.data?.error ||
          err.response?.data?.detail ||
          err.response?.data?.message ||
          err.message ||
          defaultMessage
      } else if (error instanceof Error) {
        errorMessage = error.message
      }

      toast.error(errorMessage)
      console.error('Error:', error)
    },
    [toast]
  )

  return { handleError }
}
