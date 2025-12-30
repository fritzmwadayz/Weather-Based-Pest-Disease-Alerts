import { useAuthStore } from '@/stores/auth'
import { useFarmStore } from '@/stores/farm'

/*
export const initializeApp = async () => {
  const authStore = useAuthStore()
  const farmStore = useFarmStore()

  // 1. Hydrate auth state if token exists
  if (authStore.token) {
    await authStore.hydrateUser()
  }

  // 2. Initialize farm data if authenticated
  if (authStore.isAuthenticated && authStore.userId) {
    await farmStore.initialize()
  }
}*/

export const initializeApp = async () => {
  const authStore = useAuthStore()
  
  // Only initialize if token exists
  if (authStore.token) {
    try {
      await authStore.hydrateUser()
      
      // Initialize other stores if needed
      if (authStore.isAuthenticated) {
        const farmStore = useFarmStore()
        await farmStore.initialize()
      }
    } catch (err) {
      authStore.logout()
    }
  }
}