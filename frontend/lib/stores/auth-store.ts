'use client'

import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { User } from '@/lib/api/auth'

interface AuthSession {
  tokenType: 'bearer'
}

interface AuthState {
  user: User | null
  session: AuthSession | null
  isLoading: boolean
  error: string | null
  setUser: (user: User | null) => void
  setSession: (session: AuthSession | null) => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      session: null,
      isLoading: false,
      error: null,
      setUser: (user) => set({ user }),
      setSession: (session) => set({ session }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      clearAuth: () => set({ user: null, session: null, error: null, isLoading: false }),
    }),
    {
      name: 'gasbot-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        session: state.session,
      }),
    }
  )
)
