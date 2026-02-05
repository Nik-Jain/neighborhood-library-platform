'use client'

import { useEffect, useRef } from 'react'
import { AlertCircle, X } from 'lucide-react'

interface ConfirmationDialogProps {
  isOpen: boolean
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'info'
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmationDialog({
  isOpen,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'warning',
  onConfirm,
  onCancel,
}: ConfirmationDialogProps) {
  const confirmButtonRef = useRef<HTMLButtonElement>(null)
  const dialogRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onCancel()
      }
    }
    
    // Focus trap - keep focus within dialog
    const handleTab = (e: KeyboardEvent) => {
      if (!isOpen || e.key !== 'Tab' || !dialogRef.current) return
      
      const focusableElements = dialogRef.current.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements[0] as HTMLElement
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement
      
      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault()
        lastElement?.focus()
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault()
        firstElement?.focus()
      }
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.addEventListener('keydown', handleTab)
      document.body.style.overflow = 'hidden'
      
      // Auto-focus the cancel button (safer default for destructive actions)
      setTimeout(() => confirmButtonRef.current?.focus(), 100)
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('keydown', handleTab)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onCancel])

  if (!isOpen) return null

  const variantStyles = {
    danger: {
      icon: 'text-red-600',
      button: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
    },
    warning: {
      icon: 'text-yellow-600',
      button: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500',
    },
    info: {
      icon: 'text-blue-600',
      button: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500',
    },
  }

  const styles = variantStyles[variant]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" role="dialog" aria-modal="true" aria-labelledby="dialog-title">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onCancel}
        aria-hidden="true"
      />
      
      {/* Dialog */}
      <div ref={dialogRef} className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 animate-in fade-in zoom-in duration-200">
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex gap-4">
          <div className={`flex-shrink-0 ${styles.icon}`}>
            <AlertCircle className="w-6 h-6" />
          </div>
          
          <div className="flex-1">
            <h3 id="dialog-title" className="text-lg font-semibold text-gray-900 mb-2">
              {title}
            </h3>
            <p id="dialog-description" className="text-sm text-gray-600 mb-6">
              {message}
            </p>

            <div className="flex gap-3 justify-end">
              <button
                ref={confirmButtonRef}
                onClick={onCancel}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-colors"
                aria-label={`${cancelLabel} dialog`}
              >
                {cancelLabel}
              </button>
              <button
                onClick={() => {
                  onConfirm()
                  onCancel()
                }}
                className={`px-4 py-2 text-sm font-medium text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${styles.button}`}
                aria-label={`${confirmLabel} action`}
              >
                {confirmLabel}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
