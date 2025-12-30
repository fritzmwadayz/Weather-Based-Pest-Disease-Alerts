import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Cache object
const apiCache = {
  farmData: null,
  lastFetch: null
}

/* ==================== */
/* REQUEST INTERCEPTORS */
/* ==================== */

// Debugging interceptor
apiClient.interceptors.request.use(config => {
  console.log('🔍 Request:', config.method?.toUpperCase(), config.url)
  return config
})

// Authentication interceptor
apiClient.interceptors.request.use(config => {
  const authStore = useAuthStore()
  const token = authStore.token || localStorage.getItem('token')
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

/* ===================== */
/* RESPONSE INTERCEPTORS */
/* ===================== */

apiClient.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response?.status === 401) {
    const authStore = useAuthStore()
    authStore.logout()
    window.location.href = '/login'
  }
  return Promise.reject(error)
})

/* ================= */
/* API METHODS */
/* ================= */

const verifySession = () => {
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    throw new Error('Session expired')
  }
  return authStore.userId
}

// Consolidated data fetching
export const fetchFarmData = async (forceRefresh = false) => {
  const userId = verifySession()
  
  // Check cache first (valid for 30 seconds)
  const now = Date.now()
  if (!forceRefresh && apiCache.farmData && apiCache.lastFetch && 
      (now - apiCache.lastFetch) < 30000) {
    return apiCache.farmData
  }
  
  try {
    const response = await apiClient.get(`/api/farms/${userId}`)
    apiCache.farmData = response.data
    apiCache.lastFetch = now
    return response.data
  } catch (error) {
    console.error('Failed to fetch farm data:', error)
    throw error
  }
}

// Settings methods
export const updateGeneralSettings = async (settingsData) => {
  const userId = verifySession()
  try {
    const response = await apiClient.put(`/api/farms/${userId}/settings/general`, settingsData)
    // Update cache
    if (apiCache.farmData) {
      apiCache.farmData.settings.general = response.data
    }
    return response.data
  } catch (error) {
    console.error('Failed to update general settings:', error)
    throw error
  }
}

export const updateFarmSettings = async (settingsData) => {
  const userId = verifySession()
  try {
    const response = await apiClient.put(`/api/farms/${userId}/settings/farm`, settingsData)
    // Update cache
    if (apiCache.farmData) {
      apiCache.farmData.settings.farm = response.data
    }
    return response.data
  } catch (error) {
    console.error('Failed to update farm settings:', error)
    throw error
  }
}

// Weather methods
export const getWeatherData = async () => {
  const userId = verifySession()
  try {
    const response = await apiClient.get(`/api/farms/${userId}/weather`)
    // Update cache
    if (apiCache.farmData) {
      apiCache.farmData.weather = response.data
    }
    return response.data
  } catch (error) {
    console.error('Failed to fetch weather data:', error)
    throw error
  }
}

// Default export for legacy usage
export default apiClient