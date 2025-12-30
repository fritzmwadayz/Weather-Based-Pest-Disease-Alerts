<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFarmStore } from '@/stores/farm'
import apiClient from '@/api'

const authStore = useAuthStore()
const farmStore = useFarmStore()
const loading = ref(true) // Start in loading state
const error = ref(null)
const weatherData = ref(null)

// State management
const displayState = computed(() => {
  if (!authStore.isAuthenticated) return 'unauthenticated'
  if (loading.value) return 'loading'
  if (error.value) return 'error'
  if (weatherData.value) return 'weather'
  return 'no-data'
})

const fetchWeather = async (location) => {
  if (!location) return
  
  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get('/weather-data', {
      params: { location },
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    // Validate response structure
    if (!response.data?.current) {
      throw new Error('Invalid weather data format')
    }
    
    weatherData.value = response.data
    farmStore.weatherData = response.data
    
  } catch (err) {
    error.value = 'Failed to load weather data'
    console.error('Weather fetch error:', err)
  } finally {
    loading.value = false
  }
}

// Initialize
onMounted(async () => {
  if (farmStore.location) {
    await fetchWeather(farmStore.location)
  }
})

// Watch for location changes
watch(
  () => farmStore.location,
  (newLocation) => {
    if (newLocation) {
      fetchWeather(newLocation)
    }
  }
)
</script>

<template>
  <div class="weather-widget">
    <div v-if="displayState === 'unauthenticated'" class="auth-warning">
      Please login to view weather
    </div>
    
    <div v-else-if="displayState === 'loading'" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      Loading weather...
    </div>
    
    <div v-else-if="displayState === 'error'" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      {{ error }}
      <button @click="fetchWeather(farmStore.location)">Retry</button>
    </div>
    
    <div v-else-if="displayState === 'weather'" class="weather-display">
      <!-- Your weather display content -->
      <div class="temperature">
        {{ weatherData.current.temperature }}°C
      </div>
    </div>
    
    <div v-else class="no-data">
      No weather data available
    </div>
  </div>
</template>