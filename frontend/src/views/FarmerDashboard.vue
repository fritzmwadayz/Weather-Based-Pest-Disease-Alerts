<template>
  <div class="dashboard-layout">
    <TopNavbar />
    
    <div class="main-content">
      <SideNavbar />

        <!-- Loading and Error states remain the same -->
      <div class="content ml-64 p-6">
        <!-- Loading State -->
        <div v-if="loading" class="p-8 text-center">
          <i class="fas fa-spinner fa-spin text-2xl text-blue-500"></i>
          <p class="mt-2">Loading farm data...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="bg-red-50 p-4 rounded-lg mb-6">
          <div class="flex items-center text-red-800">
            <i class="fas fa-exclamation-circle mr-2"></i>
            <h3 class="font-medium">Data Load Error</h3>
          </div>
          <p class="text-sm mt-1 text-red-700">{{ error }}</p>
          <button @click="loadFarmData" 
                  class="mt-2 text-sm text-blue-600 hover:underline">
            Retry
          </button>
        </div>
             
        <!-- Main Content -->
        <div v-if="isDashboardRoute && !loading">
          <!-- Fixed Cards Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <!-- Summary Card (span 2 columns on larger screens) -->
            <div class="md:col-span-2">
              <SummaryCard 
                :location="farm.location"
                :crops="farm.crops"
                :last-updated="farm.lastUpdated"
                :weather="farmStore.weatherData"
              />
            </div>
            
            <!-- Weather Widget -->
            <WeatherWidget :data="weatherData" />
            
            <!-- Alert Card -->
            <AlertCard :alerts="alerts" />
          </div>
          
          <!-- Blog Cards Section -->
          <div v-if="blogPosts.length" class="mb-6">
            <h2 class="text-xl font-semibold mb-4">Recommended Articles</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <BlogCard 
                v-for="post in blogPosts" 
                :key="post.id"
                :title="post.title"
                :content="post.excerpt"
                :author="post.author"
                :date="post.date"
                :urgency="post.urgency"
                :tags="post.tags"
              />
            </div>
          </div>
        </div>
        
        <router-view v-else v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { io } from 'socket.io-client'
import TopNavbar from '@/components/TestNav.vue'
import SideNavbar from '@/components/SideNavbar.vue'
import SummaryCard from '@/components/cards/SummaryCard.vue'
import WeatherWidget from '@/components/cards/WeatherWidget.vue'
import AlertCard from '@/components/cards/AlertCard.vue'
import BlogCard from '@/components/cards/BlogCard.vue'
import {storeToRefs} from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useFarmStore } from '@/stores/farm'

//Initialize stores and router
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const farmStore = useFarmStore()

//Destructure store properties
const { isAuthenticated, fetchFarmData } = authStore
const { alerts, weatherData } = storeToRefs(farmStore)

//Component state
const farm = ref({
  location: 'Loading...',
  crops: [],
  temperature: null,
  lastUpdated: 'Never'
})
const loading = ref(true)
const error = ref(null)
const socketConnected = ref(false)
let socket = null

//Computed properties
const isDashboardRoute = computed(() => {
  return route.path === '/farmer-dashboard' || 
         route.path === '/' || 
         route.name === 'Dashboard'
})

const currentUserId = ref(1) // TODO: Replace with actual auth system

const updateFarmData = (newData) => {
  farm.value = {
    location: newData.location || 'Not specified',
    crops: newData.crops || [],
    temperature: newData.temperature,
    lastUpdated: new Date(newData.updated_at || Date.now()).toLocaleString()
  }
}

// Mock blog data - replace with actual API call
const blogPosts = ref([
  {
    id: 1,
    title: 'Managing Aphids in Maize Crops',
    excerpt: 'Learn effective strategies to control aphid infestations in your maize fields...',
    author: 'AgriExpert',
    date: '2023-05-10',
    urgency: 'high',
    tags: ['maize', 'pests', 'aphids']
  },
  {
    id: 2,
    title: 'Weather Patterns and Crop Health',
    excerpt: 'Understanding how seasonal weather changes affect your crops...',
    author: 'WeatherPro',
    date: '2023-04-28',
    urgency: 'medium',
    tags: ['weather', 'crop-health']
  }
])

// Fetch blog posts based on alerts
const fetchRecommendedPosts = async () => {
  try {
    // Get unique pest tags from alerts
    const pestTags = [...new Set(alerts.value.map(alert => alert.type))]
    
    // Call API to get relevant posts
    // const response = await apiClient.get('/blog-posts', { params: { tags: pestTags } })
    // blogPosts.value = response.data
    
    // For now using mock data
  } catch (error) {
    console.error('Failed to fetch blog posts:', error)
  }
}

const loadFarmData = async () => {
  try {
    loading.value = true
    error.value = null
    
    // Use farmStore's method
    const data = await farmStore.loadFarmData()
    
    // Update local state
    farm.value = {
      location: data.location || 'Not specified',
      crops: data.crops || [],
      temperature: data.temperature,
      lastUpdated: new Date(data.updated_at || Date.now()).toLocaleString()
    }
  } catch (err) {
    error.value = err.message
    console.error('Data load error:', err)
    
    // Redirect if unauthorized
    if (err.message.includes('Session expired') || err.message.includes('Authentication required')) {
      router.push('/login')
    }
  } finally {
    loading.value = false
  }
}

const initializeSocket = () => {
  if (!socket) {
    try {
      socket = io('http://localhost:5000', {
        reconnectionAttempts: 3,
        timeout: 5000,
        withCredentials: true,
        transports: ['websocket']  // Force WebSocket transport
      });
      
      socket.on('connect', () => {
        console.log('Socket connected!');  // Debug log
        socketConnected.value = true;
      });
      
      // ... rest of your socket handlers ...
    } catch (err) {
      console.error('Socket init error:', err);
    }
  }
};

import { debounce } from 'lodash'

/*
onMounted(debounce(() => {
  farmStore.fetchFarmData()
}, 500)) 
*/

onMounted(debounce (async () => {
  try {
    // First ensure user is authenticated
    await authStore.hydrateUser()
    
    // Then load farm data
    if (authStore.user?.id) {
      await farmStore.loadFarmData()
    } else {
      router.push('/login')
    }
  } catch (err) {
    console.error('Initialization error:', err)
  }
  console.log('Current token:', authStore.token)
  console.log('Current user ID:', authStore.user?.id)
},500))

onBeforeUnmount(() => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
})

// Watch for route changes
watch(
  () => route.path,
  (newPath) => {
    if (isDashboardRoute.value) {
      initializeSocket()
      loadFarmData()
    } else if (socket) {
      socket.disconnect()
      socket = null
    }
  }
)
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  display: flex;
  flex: 1;
}

.content {
  flex: 1;
  margin-left: 16rem;
  padding: 1.5rem;
  transition: margin-left 0.3s ease;
}
</style>