import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../services/api'

export interface User {
  user_id: string
  email: string
  name: string
  role: 'PARTICIPANT' | 'ORGANIZER' | 'JUDGE'
  team_id?: string
  created_at: string
  updated_at: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string, role: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing token in localStorage on mount
    const savedToken = localStorage.getItem('token')
    if (savedToken) {
      setToken(savedToken)
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      
      // Fetch user profile
      api.get('/auth/me')
        .then(response => {
          setUser(response.data)
        })
        .catch(() => {
          // Token is invalid, remove it
          localStorage.removeItem('token')
          setToken(null)
          delete api.defaults.headers.common['Authorization']
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { user: userData, tokens } = response.data
      
      setUser(userData)
      setToken(tokens.access_token)
      
      // Store token in localStorage
      localStorage.setItem('token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      
      // Set authorization header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const register = async (email: string, password: string, name: string, role: string) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
        name,
        role: role.toUpperCase()
      })
      const { user: userData, tokens } = response.data
      
      setUser(userData)
      setToken(tokens.access_token)
      
      // Store token in localStorage
      localStorage.setItem('token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      
      // Set authorization header for future requests
      api.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed')
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    
    // Remove tokens from localStorage
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    
    // Remove authorization header
    delete api.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    token,
    login,
    register,
    logout,
    loading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}