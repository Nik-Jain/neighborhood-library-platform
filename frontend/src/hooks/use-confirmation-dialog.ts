'use client'

import { useState, useCallback, useRef } from 'react'

interface ConfirmationOptions {
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  variant?: 'danger' | 'warning' | 'info'
}

interface ConfirmationDialogState extends ConfirmationOptions {
  isOpen: boolean
  onConfirm: () => void
}

export function useConfirmationDialog() {
  const [dialogState, setDialogState] = useState<ConfirmationDialogState>({
    isOpen: false,
    title: '',
    message: '',
    onConfirm: () => {},
  })
  
  // Store the promise resolver to call it from handleCancel
  const resolveRef = useRef<((value: boolean) => void) | null>(null)

  const confirm = useCallback((options: ConfirmationOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      resolveRef.current = resolve
      
      setDialogState({
        ...options,
        isOpen: true,
        onConfirm: () => {
          resolve(true)
          resolveRef.current = null
          setDialogState(prev => ({ ...prev, isOpen: false }))
        },
      })
    })
  }, [])

  const handleCancel = useCallback(() => {
    // Resolve the promise with false when canceling
    if (resolveRef.current) {
      resolveRef.current(false)
      resolveRef.current = null
    }
    setDialogState(prev => ({ ...prev, isOpen: false }))
  }, [])

  return {
    dialogState,
    confirm,
    handleCancel,
  }
}
