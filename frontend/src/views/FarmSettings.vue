<template>
  <div class="p-6 max-w-lg mx-auto bg-white shadow-md rounded-md">
    <h2 class="text-2xl font-bold mb-4">Farm Settings</h2>

    <form @submit.prevent="saveFarmSettings" class="space-y-4">
      <!-- Crops Selection -->
      <div class="block">
        <label class="font-medium">Crops:</label>
        <div class="mt-2 space-y-2">
          <div v-for="crop in availableCrops" :key="crop" class="flex items-center">
            <input 
              type="checkbox" 
              :id="crop" 
              :value="crop" 
              v-model="selectedCrops"
              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
            >
            <label :for="crop" class="ml-2 block text-sm text-gray-700 capitalize">
              {{ crop }}
            </label>
          </div>
        </div>
      </div>

      <!-- Location Selection -->
      <div class="block">
        <label class="font-medium">Location:</label>
        <select 
          v-model="location" 
          class="mt-1 block w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500"
          required
        >
          <option value="" disabled>Select your location</option>
          <option 
            v-for="(weather, loc) in locationOptions" 
            :key="loc" 
            :value="loc"
          >
            {{ loc }} (Avg: {{ weather.temperature }}°C)
          </option>
        </select>
      </div>

      <button 
        type="submit" 
        class="w-full bg-green-600 text-white p-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
        :disabled="isSaving || !isFormValid"
      >
        <span v-if="isSaving">Saving...</span>
        <span v-else>Save Settings</span>
      </button>
    </form>

    <!-- Status Messages -->
    <div v-if="message" class="mt-4 p-4 bg-green-100 text-green-700 rounded-md">
      <p>{{ message }}</p>
    </div>

    <div v-if="error" class="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useFarmStore } from '@/stores/farm'
import apiClient from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const farmStore = useFarmStore()

//Form data
const selectedCrops = ref([])
const location = ref('')
const isSaving = ref(false)
const message = ref('')
const error = ref('')

//isFormValid computed property
const isFormValid = computed(() => {
  return selectedCrops.value.length > 0 && location.value
})

// Available options
const availableCrops = ['maize', 'wheat', 'rice']
const locationOptions = ref({
  "Nairobi": {"temperature": 25, "humidity": 70, "rainfall": 120, "wind_speed": 10},
  "Taita Hills": {"temperature": 22, "humidity": 75, "rainfall": 200, "wind_speed": 8},
  "Kisumu": {"temperature": 28, "humidity": 80, "rainfall": 180, "wind_speed": 12},
  "Mombasa": {"temperature": 30, "humidity": 85, "rainfall": 220, "wind_speed": 15}
})

onMounted(async () => {
  try {
    if (!authStore.isAuthenticated) {
      error.value = 'Please login to continue'
      return
    }

    // Load settings
    const response = await apiClient.get(`/farm-settings/${authStore.userId}`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })
    
    if (response.data) {
      location.value = response.data.location
      selectedCrops.value = response.data.crops || []
      // Update store
      farmStore.updateSettings({
        location: response.data.location,
        crops: response.data.crops
      })
    }
  } catch (err) {
    console.error('Error loading settings:', err)
    error.value = 'Failed to load settings'
    if (err.response?.status === 401) {
      authStore.logout()
    }
  }
})

const saveFarmSettings = async () => {
  if (!isFormValid.value) return
  
  isSaving.value = true
  error.value = ''
  message.value = ''

  try {
    await apiClient.put('/farm-settings', {
      user_id: authStore.userId,
      crops: selectedCrops.value,
      location: location.value
    }, {
      headers: {
        Authorization: `Bearer ${authStore.token}`
      }
    })

    // Update store
    farmStore.updateSettings({
      location: location.value,
      crops: selectedCrops.value
    })

    message.value = 'Settings saved successfully'
    setTimeout(() => router.push('/farmer-dashboard'), 1500)
  } catch (err) {
    error.value = err.response?.data?.message || 'Failed to save settings'
    if (err.response?.status === 401) {
      authStore.logout()
    }
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>

</style>