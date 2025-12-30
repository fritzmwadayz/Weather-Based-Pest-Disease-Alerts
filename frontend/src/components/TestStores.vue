<template>
  <div class="store-tester">
    <h2>Farm Endpoint Tester</h2>
    
    <div class="auth-status">
      Status: {{ authStore.isAuthenticated ? '✅ Authenticated' : '❌ Not authenticated' }}
      <span v-if="authStore.user">(User ID: {{ authStore.user.id }})</span>
    </div>
    
    <div class="auth-actions">
      <button @click="testLogin">Test Login</button>
      <button @click="testLogout">Test Logout</button>
      <button @click="testFetchUser">Test Fetch User</button>
    </div>
    
    <div v-if="loading" class="loading">Loading...</div>
    <div v-if="error" class="error">{{ error }}</div>
    
    <div class="test-actions">
      <button @click="testGetSettings" :disabled="!authStore.isAuthenticated">
        Test /get-settings
      </button>
      <button @click="testFarmData" :disabled="!authStore.isAuthenticated">
      Test Farm Data Endpoint
      </button>
      <button @click="testWeather">Test Weather</button>
      <button @click="testAlerts" :disabled="!authStore.isAuthenticated">
        Test Alerts
      </button>
    </div>
    
    <div v-if="results" class="results">
      <h3>Results:</h3>
      <pre>{{ JSON.stringify(results, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import apiClient from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useFarmStore } from '@/stores/farm'

const authStore = useAuthStore()
const farmStore = useFarmStore()
const loading = ref(false)
const error = ref(null)
const results = ref(null)

const testWeather = async () => {
  loading.value = true
  error.value = null
  try {
    // First ensure we have a location
    if (!farmStore.location) {
      await farmStore.fetchAllData()
    }
    
    // Make direct API call to verify endpoint
    const response = await apiClient.get('/weather-data', {
      params: {
        location: farmStore.location || 'Nairobi' // Fallback location
      }
    })
    
    results.value = {
      apiResponse: response.data,
      storeData: {
        current: farmStore.currentConditions,
        forecast: farmStore.forecast
      }
    }
  } catch (err) {
    error.value = `Weather request failed: ${err.response?.data?.message || err.message}`
    console.error('Weather error details:', {
      config: err.config,
      response: err.response
    })
  } finally {
    loading.value = false
  }
}

const testFarmData = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const userId = authStore.user?.id;
    if (!userId) throw new Error('User not authenticated');

    const response = await apiClient.get(`/api/farms/${userId}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      },
      withCredentials: true
    });

    results.value = {
      apiResponse: response.data,
      storeData: {
        location: farmStore.location,
        crops: farmStore.crops
      }
    };

    // Update store if needed
    if (response.data.data) {
      farmStore.location = response.data.data.location;
      farmStore.crops = response.data.data.crops;
    }

  } catch (err) {
    error.value = `Farm data request failed: ${err.response?.data?.message || err.message}`;
    console.error('Error details:', {
      url: err.config?.url,
      status: err.response?.status,
      error: err.response?.data || err.message
    });
  } finally {
    loading.value = false;
  }
}

const testEndpoint = async (method, url, data = null) => {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient({
      method,
      url,
      data,
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    results.value = response.data
  } catch (err) {
    error.value = err.response?.data?.message || err.message
    if (err.response?.status === 401) {
      authStore.logout(false) // Pass false to prevent redirect
    }
  } finally {
    loading.value = false
  }
}

const testLogin = async () => {
  loading.value = true
  error.value = null
  try {
    const success = await authStore.login({
      email: 'test@test.com',
      password: 'test'
    }, false) // Pass false to prevent redirect
    
    if (!success) {
      error.value = 'Login failed - check credentials'
    } else {
      results.value = { status: 'Login successful', user: authStore.user }
    }
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const testLogout = () => {
  authStore.logout(false) // Pass false to prevent redirect
  results.value = { status: 'Logged out' }
}

const testFetchUser = async () => {
  try {
    await authStore.fetchUser()
    results.value = { user: authStore.user }
  } catch (err) {
    error.value = 'Failed to fetch user: ' + err.message
  }
}

const testGetSettings = () => {
  if (!authStore.user?.id) {
    error.value = 'No user ID available'
    return
  }
  testEndpoint('get', `/get-settings/${authStore.user.id}`)
}

</script>

<style scoped>
.auth-status {
  margin: 1rem 0;
  padding: 0.5rem;
  background: #f0f8ff;
  border-radius: 4px;
}

.auth-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.loading { 
  color: blue; 
  margin: 1rem 0; 
}

.error { 
  color: red; 
  margin: 1rem 0; 
  padding: 0.5rem;
  background: #fff0f0;
  border-radius: 4px;
}

.test-actions { 
  display: flex; 
  gap: 1rem; 
  margin: 1rem 0; 
}

button { 
  padding: 0.5rem 1rem; 
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

button:hover:not(:disabled) {
  background: #e0e0e0;
}

.results { 
  margin-top: 2rem; 
  text-align: left; 
}

pre { 
  background: #f5f5f5; 
  padding: 1rem; 
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}
</style>