import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const isLoading = ref(false)
  const error = ref(null)
  const role = ref(localStorage.getItem('role'))
  
  // Debugging utility
  const debug = (message, data = null) => {
    console.log(`[AuthStore] ${message}`, data)
  }

  // Getters
  const isAuthenticated = computed(() => {
    const authenticated = !!token.value
    debug('Authentication check', { authenticated })
    return authenticated
  })

  const userId = computed(() => user.value?.id)

  // Save auth state to localStorage
  const persistAuth = () => {
    if (token.value) localStorage.setItem('token', token.value)
    if (refreshToken.value) localStorage.setItem('refreshToken', refreshToken.value)
    if (role.value) localStorage.setItem('role', role.value)
  }

  // Clear auth state
  const clearAuth = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('role')
  }

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null
      debug('Login attempt', { email: credentials.email })

      const response = await apiClient.post('/login', {
        email: credentials.email.toLowerCase(),
        password: credentials.password
      })

      debug('Login response', response.data)

      if (!response.data?.token) throw new Error('No token received')
      if (!response.data?.user) throw new Error('No user data received')

      token.value = response.data.token
      refreshToken.value = response.data.refreshToken || response.data.token
      user.value = response.data.user
      role.value = response.data.user?.role

      persistAuth()
      debug('Login successful', { userId: user.value?.id })
      return true
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      debug('Login failed', { error: error.value })
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    debug('Logging out')
    token.value = null
    refreshToken.value = null
    user.value = null
    role.value = null
    error.value = null
    clearAuth()
    router.push('/login')
  }

  const attemptTokenRefresh = async () => {
    if (!refreshToken.value) {
      debug('No refresh token available')
      return false
    }

    try {
      debug('Attempting token refresh')
      const response = await apiClient.post('/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${refreshToken.value}` }
      })

      if (!response.data?.access_token) {
        throw new Error('No new token received')
      }

      token.value = response.data.access_token
      persistAuth()
      debug('Token refresh successful')
      return true
    } catch (err) {
      debug('Token refresh failed', { error: err.message })
      logout()
      return false
    }
  }

  const hydrateUser = async () => {
    if (!token.value) {
      debug('Skipping hydration - no token')
      return false
    }

    try {
      isLoading.value = true
      error.value = null
      debug('Starting hydration', { token: token.value.substring(0, 10) + '...' })

      // First try to get user data from consolidated endpoint
      try {
        const farmResponse = await apiClient.get(`/api/farms/${user.value?.id}`)
        
        if (farmResponse.data?.user) {
          user.value = farmResponse.data.user
          role.value = farmResponse.data.user.role
          debug('Hydration successful via farm endpoint', { userId: user.value?.id })
          return true
        }
      } catch (initialError) {
        debug('Initial hydration via farm endpoint failed', { error: initialError.message })
      }

      // Fallback to auth/me if needed
      try {
        const userResponse = await apiClient.get('/auth/me')
        if (userResponse.data?.id) {
          user.value = userResponse.data
          role.value = userResponse.data.role
          debug('Hydration successful via auth/me', { userId: user.value?.id })
          return true
        }
      } catch (fallbackError) {
        debug('Fallback hydration failed', { error: fallbackError.message })
      }

      throw new Error('Could not retrieve user data')
    } catch (err) {
      error.value = `Hydration failed: ${err.message}`
      debug('Hydration error', { error: error.value })

      if (err.message.includes('expired') || err.message.includes('invalid')) {
        debug('Clearing invalid session')
        logout()
      }

      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { 
    // State
    user,
    token,
    isLoading,
    error,
    role,
    
    // Getters
    isAuthenticated,
    userId,
    
    // Actions
    login,
    logout,
    hydrateUser,
    attemptTokenRefresh
  }
})

/*
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref(null)
  const role = ref(localStorage.getItem('role'))
  
  // Debugging utility
  const debug = (message, data = null) => {
    console.log(`[AuthStore] ${message}`, data)
  }

  // Getters
  const isAuthenticated = computed(() => {
    const authenticated = !!token.value
    debug('Authentication check', { authenticated })
    return authenticated
  })

  const login = async (credentials) => {
    try {
      isLoading.value = true
      error.value = null
      debug('Login attempt', { email: credentials.email })

      const response = await apiClient.post('/login', {
        email: credentials.email.toLowerCase(),
        password: credentials.password
      })

      debug('Login response', { 
        hasToken: !!response.data?.token,
        hasUser: !!response.data?.user 
      })

      if (!response.data?.token) throw new Error('No token received')
      if (!response.data?.user) throw new Error('No user data received')

      token.value = response.data.token
      user.value = response.data.user
      role.value = response.data.user?.role

      localStorage.setItem('token', token.value)
      if (role.value) localStorage.setItem('role', role.value)

      debug('Login successful', { userId: user.value?.id })
      return true
    } catch (err) {
      error.value = err.response?.data?.message || err.message
      debug('Login failed', { error: error.value })
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const logout = () => {
    debug('Logging out')
    token.value = null
    user.value = null
    role.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    router.push('/login')
  }

  const hydrateUser = async () => {
    if (!token.value) {
      debug('Skipping hydration - no token')
      return false
    }

    try {
      isLoading.value = true
      debug('Starting hydration', { token: token.value.substring(0, 10) + '...' })

      // Use the existing /auth/me endpoint instead of /auth/validate
      const response = await apiClient.get('/auth/me', {
        headers: { Authorization: `Bearer ${token.value}` },
        validateStatus: (status) => status < 500 // Don't throw for 401/403
      })

      debug('Hydration response', { 
        status: response.status,
        data: response.data 
      })

      if (response.status === 401 || response.status === 404) {
        throw new Error('Session invalid or endpoint not found')
      }

      if (!response.data?.id) {
        throw new Error('Invalid user data structure')
      }

      user.value = response.data
      role.value = response.data.role

      debug('Hydration successful', { userId: user.value?.id })
      return true
    } catch (err) {
      error.value = `Hydration failed: ${err.message}`
      debug('Hydration error', { error: error.value })

      // Clear invalid session
      if (err.message.includes('invalid') || err.message.includes('not found')) {
        debug('Clearing invalid session')
        logout()
      }

      throw err
    } finally {
      isLoading.value = false
    }
  }

  return { 
    user,
    token,
    isLoading,
    error,
    role,
    isAuthenticated,
    login,
    logout,
    hydrateUser
  }
})
*/