<template>
  <div class="summary-card bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Card Header -->
    <div class="card-header bg-green-50 px-6 py-4 border-b border-gray-100">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">
          <i class="fas fa-tractor text-green-500 mr-2"></i>
          Farm Summary
        </h3>
        <span class="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
          {{ lastUpdatedText }}
        </span>
      </div>
    </div>

    <!-- Card Body -->
    <div class="card-body p-6">
      <!-- Location Section -->
      <div class="mb-5">
        <div class="flex items-center text-gray-500 mb-1">
          <i class="fas fa-map-marker-alt mr-2 text-sm"></i>
          <span class="text-xs font-medium uppercase tracking-wider">Location</span>
        </div>
        <p class="text-gray-800 font-medium">{{ location || 'Not specified' }}</p>
        
        <!-- Weather snippet if location exists -->
        <div v-if="weather && location" class="mt-2 flex items-center text-sm text-gray-500">
          <i :class="weatherIcon" class="mr-1"></i>
          <span>{{ weather.temperature }}°C, {{ weather.condition }}</span>
        </div>
      </div>

      <!-- Crops Section -->
      <div class="mb-5">
        <div class="flex items-center text-gray-500 mb-1">
          <i class="fas fa-seedling mr-2 text-sm"></i>
          <span class="text-xs font-medium uppercase tracking-wider">Crops</span>
        </div>
        
        <div v-if="crops.length" class="flex flex-wrap gap-2">
          <span 
            v-for="(crop, index) in crops" 
            :key="index"
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
            :class="getCropColor(crop)"
          >
            {{ crop }}
            <span v-if="hasAlerts(crop)" class="ml-1 w-2 h-2 rounded-full bg-red-500"></span>
          </span>
        </div>
        <p v-else class="text-gray-400 text-sm italic">No crops registered</p>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Alerts</p>
          <p class="text-lg font-semibold" :class="alertCount > 0 ? 'text-red-500' : 'text-green-500'">
            {{ alertCount }}
          </p>
        </div>
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Models</p>
          <p class="text-lg font-semibold text-gray-800">{{ cropModels.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useFarmStore } from '@/stores/farm';
import { storeToRefs } from 'pinia';

const farmStore = useFarmStore();
const { alerts, weatherData } = storeToRefs(farmStore);

const props = defineProps({
  location: {
    type: String,
    default: ''
  },
  crops: {
    type: Array,
    default: () => []
  },
  lastUpdated: {
    type: String,
    default: ''
  },
  weather: {
    type: Object,
    default: null
  }
});

const lastUpdatedText = computed(() => {
  if (!props.lastUpdated) return 'Never updated';
  const now = new Date();
  const updated = new Date(props.lastUpdated);
  const diffHours = Math.floor((now - updated) / (1000 * 60 * 60));
  
  if (diffHours < 1) return 'Updated recently';
  if (diffHours < 24) return 'Updated today';
  return `Updated ${Math.floor(diffHours / 24)} days ago`;
});

const weatherIcon = computed(() => {
  if (!props.weather) return 'fas fa-question text-gray-400';
  const condition = props.weather.condition.toLowerCase();
  if (condition.includes('rain')) return 'fas fa-cloud-rain text-blue-400';
  if (condition.includes('cloud')) return 'fas fa-cloud text-gray-400';
  return 'fas fa-sun text-yellow-400';
});

const alertCount = computed(() => {
  return alerts.value.length;
});

const cropModels = computed(() => {
  // This should be replaced with actual model data from your store
  return props.crops.map(crop => ({ name: crop, status: 'active' }));
});

const getCropColor = (crop) => {
  const colors = [
    'bg-green-100 text-green-800',
    'bg-blue-100 text-blue-800',
    'bg-yellow-100 text-yellow-800',
    'bg-purple-100 text-purple-800'
  ];
  const index = props.crops.indexOf(crop) % colors.length;
  return colors[index];
};

/*const hasAlerts = (crop) => {
  return alerts.value.some(alert => alert.crop === crop);
}; */
const hasAlerts = (crop) => {
  if (!alerts.value) return false // Handle null case
  return alerts.value.some(alert => alert?.crop === crop) // Optional chaining for alert object
}
</script>

<style scoped>
.summary-card {
  /*transition: all 0.3s ease;
  &:hover {
    @apply shadow-md;
    transform: translateY(-2px);
  }*/
  transition: all 0.3s ease;
  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    transform: translateY(-2px);
  }
}
</style>