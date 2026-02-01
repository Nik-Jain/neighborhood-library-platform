import { create } from 'zustand'

interface User {
  id: string
  username: string
  email: string
  groups?: string[]
  first_name?: string
  last_name?: string
  full_name?: string
}

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  logout: () => void
  loadFromStorage: () => void
  isAdmin: () => boolean
  isLibrarian: () => boolean
  isAdminOrLibrarian: () => boolean
  isMember: () => boolean
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  setAuth: (user, token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('authToken', token)
      localStorage.setItem('user', JSON.stringify(user))
    }
    set({ user, token, isAuthenticated: true })
  },
  
  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
    }
    set({ user: null, token: null, isAuthenticated: false })
  },
  
  loadFromStorage: () => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('authToken')
      const userStr = localStorage.getItem('user')
      
      if (token && userStr) {
        const user = JSON.parse(userStr)
        set({ user, token, isAuthenticated: true })
      }
    }
  },

  isAdmin: () => {
    const { user } = get()
    return user?.groups?.includes('ADMIN') || false
  },

  isLibrarian: () => {
    const { user } = get()
    return user?.groups?.includes('LIBRARIAN') || false
  },

  isAdminOrLibrarian: () => {
    const { user } = get()
    return user?.groups?.some(g => g === 'ADMIN' || g === 'LIBRARIAN') || false
  },

  isMember: () => {
    const { user } = get()
    return user?.groups?.includes('MEMBER') || false
  },
}))
