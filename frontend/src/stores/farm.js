import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { fetchFarmData, getWeatherData } from '@/api'
import { useAuthStore } from './auth'
import { io } from 'socket.io-client'

export const useFarmStore = defineStore('farm', () => {
  // State
  const farmData = ref(null)
  const isLoading = ref(false)
  const error = ref(null)
  
  // Get auth store instance
  const authStore = useAuthStore()

  // Getters (computed properties)
  const location = computed(() => farmData.value?.location || null)
  const crops = computed(() => farmData.value?.crops || [])
  const weather = computed(() => farmData.value?.weather || null)
  const alerts = computed(() => farmData.value?.alerts || [])
  const blogRecommendations = computed(() => farmData.value?.recommendations || [])
  const lastUpdated = computed(() => farmData.value?.last_updated || null)
  const settings = computed(() => farmData.value?.settings || {})
  
  const riskLevel = computed(() => {
    return alerts.value.length > 5 ? 'critical' :
           alerts.value.length > 2 ? 'high' :
           alerts.value.length > 0 ? 'medium' : 'low'
  })

  const currentConditions = computed(() => {
    return weather.value?.current || null
  })

  const forecast = computed(() => {
    return weather.value?.forecast?.slice(0, 3) || []
  })

  // Actions
  const loadFarmData = async (forceRefresh = false) => {
    isLoading.value = true
    error.value = null
    
    try {
      if (!authStore.isAuthenticated) {
        await authStore.hydrateUser()
      }

      const data = await fetchFarmData(authStore.userId, forceRefresh)
      farmData.value = data
      return data
    } catch (err) {
      error.value = err.message
      if (err.response?.status === 401) authStore.logout()
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateSettings = async (newSettings) => {
    try {
      // This would call your API endpoint to update settings
      // Then refresh the farm data
      await loadFarmData(true)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const refreshWeatherData = async () => {
    try {
      const data = await getWeatherData()
      if (data && farmData.value) {
        farmData.value.weather = data
      }
      return data
    } catch (err) {
      console.error('Weather refresh failed:', err)
      throw err
    }
  }

  const setupWebSocket = () => {
    const socket = io(import.meta.env.VITE_WS_URL, {
      auth: { 
        token: authStore.token 
      }
    })

    socket.on('weather_update', (data) => {
      if (farmData.value) {
        farmData.value.weather = data
      }
    })

    socket.on('new_alert', (alert) => {
      if (farmData.value) {
        farmData.value.alerts = [alert, ...farmData.value.alerts]
      }
    })
  }

  const initialize = async () => {
    await loadFarmData()
    setupWebSocket()
  }

  return {
    // State
    farmData,
    isLoading,
    error,
    
    // Getters
    location,
    crops,
    weather,
    alerts,
    blogRecommendations,
    lastUpdated,
    settings,
    riskLevel,
    currentConditions,
    forecast,
    
    // Actions
    loadFarmData,
    updateSettings,
    refreshWeatherData,
    initialize
  }
})