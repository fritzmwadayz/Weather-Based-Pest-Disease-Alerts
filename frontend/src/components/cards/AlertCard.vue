<template>
  <div class="alert-card bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
    <div class="card-header bg-red-50 px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">
          <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
          Pest Alerts
        </h3>
        <span class="risk-badge px-3 py-1 rounded-full text-sm font-medium" :class="riskLevelClass">
          {{ riskLevel }}
        </span>
      </div>
    </div>

    <div class="card-body p-6">
      <div v-if="alerts.length" class="space-y-4">
        <div v-for="alert in alerts" :key="alert.id" class="alert-item p-4 rounded-lg" :class="alertItemClass(alert)">
          <div class="flex items-start">
            <div class="alert-icon mr-3 mt-1" :class="alertIconClass(alert)"></div>
            <div>
              <h4 class="font-medium text-gray-800">{{ alert.crop }}: {{ alert.name }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ alert.message }}</p>
              <div class="mt-2 flex flex-wrap gap-2">
                <span v-for="(action, idx) in alert.actions" :key="idx" 
                      class="text-xs px-2 py-1 rounded bg-blue-50 text-blue-800">
                  {{ action }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="no-alerts text-center py-8 text-gray-400">
        <i class="fas fa-check-circle text-green-400 text-3xl mb-2"></i>
        <p>No active pest alerts detected</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useFarmStore } from '@/stores/farm'
import { storeToRefs } from 'pinia'

const farmStore = useFarmStore()
const { alerts } = storeToRefs(farmStore)

const riskLevel = computed(() => {
  if (!alerts.value?.length) return 'None'
  const criticalCount = alerts.value.filter(a => a.severity === 'critical').length
  if (criticalCount > 0) return 'Critical'
  if (alerts.value.length > 3) return 'High'
  return 'Medium'
})

const riskLevelClass = computed(() => {
  return {
    'None': 'bg-green-100 text-green-800',
    'Critical': 'bg-red-100 text-red-800',
    'High': 'bg-orange-100 text-orange-800',
    'Medium': 'bg-yellow-100 text-yellow-800'
  }[riskLevel.value]
})

const alertItemClass = (alert) => {
  return {
    'critical': 'bg-red-50 border-l-4 border-red-500',
    'high': 'bg-orange-50 border-l-4 border-orange-500',
    'medium': 'bg-yellow-50 border-l-4 border-yellow-500'
  }[alert.severity] || 'bg-gray-50 border-l-4 border-gray-300'
}

const alertIconClass = (alert) => {
  return {
    'critical': 'fas fa-bug text-red-500',
    'high': 'fas fa-bug text-orange-500',
    'medium': 'fas fa-bug text-yellow-500'
  }[alert.severity] || 'fas fa-bug text-gray-400'
}
</script>

<style scoped>
.alert-card {
  transition: all 0.3s ease;
}

.alert-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.alert-icon {
  font-size: 1.25rem;
}
</style>