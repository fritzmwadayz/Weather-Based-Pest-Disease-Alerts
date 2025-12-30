import { setActivePinia, createPinia } from 'pinia'
import { useFarmStore } from '@/stores/farm'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api'
import { io } from 'socket.io-client'

// Mock the modules
vi.mock('@/api')
vi.mock('socket.io-client')

describe('Farm Store', () => {
  let farmStore, authStore

  // Sample mock data
  const mockFarmData = {
    farm: {
      location: 'Test Farm',
      crops: ['Corn', 'Wheat'],
      weather: {
        current: { temp: 72, condition: 'Sunny' },
        forecast: [
          { day: 1, temp: 70 },
          { day: 2, temp: 68 }
        ]
      },
      alerts: {
        pests: [{ id: 1, type: 'pest', name: 'Aphids' }],
        diseases: [{ id: 2, type: 'disease', name: 'Rust' }]
      }
    },
    recommendations: [
      { id: 1, title: 'Pest Control Tips' }
    ]
  }

  beforeEach(() => {
    // Create fresh pinia instance
    setActivePinia(createPinia())
    
    // Initialize stores
    farmStore = useFarmStore()
    authStore = useAuthStore()
    
    // Set mock user
    authStore.user = { id: 1, username: 'testuser' }
    authStore.token = 'mock-token'
    
    // Reset all mocks
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should initialize with default values', () => {
      expect(farmStore.location).toBeNull()
      expect(farmStore.crops).toEqual([])
      expect(farmStore.weatherData).toBeNull()
      expect(farmStore.pestAlerts).toEqual([])
      expect(farmStore.diseaseAlerts).toEqual([])
      expect(farmStore.blogRecommendations).toEqual([])
      expect(farmStore.isLoading).toBe(false)
      expect(farmStore.lastUpdated).toBeNull()
      expect(farmStore.error).toBeNull()
    })
  })

  describe('Getters', () => {
    beforeEach(() => {
      // Set some mock data for getter tests
      farmStore.pestAlerts = [{ id: 1 }, { id: 2 }]
      farmStore.diseaseAlerts = [{ id: 3 }]
      farmStore.weatherData = {
        current: { temp: 72 },
        forecast: [{ day: 1, temp: 70 }, { day: 2, temp: 68 }]
      }
    })

    it('should calculate correct risk level', () => {
      expect(farmStore.riskLevel).toBe('high') // 3 total alerts
      
      farmStore.diseaseAlerts = []
      expect(farmStore.riskLevel).toBe('medium')
      
      farmStore.pestAlerts = []
      expect(farmStore.riskLevel).toBe('low')
    })

    it('should return current weather conditions', () => {
      expect(farmStore.currentConditions).toEqual({ temp: 72 })
    })

    it('should return forecast data', () => {
      expect(farmStore.forecast).toHaveLength(2)
      expect(farmStore.forecast[0].day).toBe(1)
    })
  })

  describe('Actions', () => {
    describe('fetchAllData', () => {
      it('should fetch and store all farm data', async () => {
        // Mock API response
        apiClient.get.mockResolvedValue({ data: mockFarmData })
        
        await farmStore.fetchAllData()
        
        // Verify API call
        expect(apiClient.get).toHaveBeenCalledWith('/get-settings/1')
        
        // Verify state updates
        expect(farmStore.location).toBe('Test Farm')
        expect(farmStore.crops).toEqual(['Corn', 'Wheat'])
        expect(farmStore.weatherData).toEqual(mockFarmData.farm.weather)
        expect(farmStore.pestAlerts).toEqual([{ id: 1, type: 'pest', name: 'Aphids' }])
        expect(farmStore.blogRecommendations).toEqual([{ id: 1, title: 'Pest Control Tips' }])
        expect(farmStore.lastUpdated).toBeInstanceOf(Date)
        expect(farmStore.isLoading).toBe(false)
      })

      it('should handle errors', async () => {
        apiClient.get.mockRejectedValue(new Error('Network error'))
        
        await farmStore.fetchAllData()
        
        expect(farmStore.error).toBe('Network error')
        expect(farmStore.isLoading).toBe(false)
      })

      it('should logout on 401 error', async () => {
        const error = new Error('Unauthorized')
        error.response = { status: 401 }
        apiClient.get.mockRejectedValue(error)
        authStore.logout = vi.fn()
        
        await farmStore.fetchAllData()
        
        expect(authStore.logout).toHaveBeenCalled()
      })
    })

    describe('updateSettings', () => {
      it('should update farm settings', async () => {
        const mockResponse = {
          data: {
            farm_settings: {
              location: 'New Location',
              crops: ['Soybean']
            }
          }
        }
        apiClient.put.mockResolvedValue(mockResponse)
        
        const result = await farmStore.updateSettings({
          location: 'New Location',
          crops: ['Soybean']
        })
        
        expect(result).toBe(true)
        expect(apiClient.put).toHaveBeenCalledWith('/get-settings', {
          location: 'New Location',
          crops: ['Soybean'],
          user_id: 1
        })
        expect(farmStore.location).toBe('New Location')
        expect(farmStore.crops).toEqual(['Soybean'])
      })
    })

    describe('initialize', () => {
      it('should fetch data and setup websocket', () => {
        farmStore.fetchAllData = vi.fn()
        farmStore.setupWebSocket = vi.fn()
        
        farmStore.initialize()
        
        expect(farmStore.fetchAllData).toHaveBeenCalled()
        expect(farmStore.setupWebSocket).toHaveBeenCalled()
      })
    })

    describe('WebSocket Setup', () => {
      it('should handle weather updates', () => {
        farmStore.setupWebSocket()
        
        // Get the mock socket instance
        const mockSocket = io.mock.results[0].value
        
        // Find the weather update handler
        const weatherHandler = mockSocket.on.mock.calls.find(
          call => call[0] === 'weather_update'
        )[1]
        
        // Test the handler
        weatherHandler({ temp: 75, condition: 'Cloudy' })
        expect(farmStore.weatherData).toEqual({ temp: 75, condition: 'Cloudy' })
      })

      it('should handle new pest alerts', () => {
        farmStore.setupWebSocket()
        const mockSocket = io.mock.results[0].value
        
        const alertHandler = mockSocket.on.mock.calls.find(
          call => call[0] === 'new_alert'
        )[1]
        
        alertHandler({ id: 1, type: 'pest', name: 'Locust' })
        expect(farmStore.pestAlerts).toEqual([
          { id: 1, type: 'pest', name: 'Locust' }
        ])
      })
    })
  })
})