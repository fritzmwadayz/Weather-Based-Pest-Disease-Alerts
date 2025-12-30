<template>
  <div class="bg-white rounded-lg shadow overflow-hidden h-full flex flex-col"
       :class="{
         'border-l-4 border-green-500': urgency === 'low',
         'border-l-4 border-yellow-500': urgency === 'medium',
         'border-l-4 border-red-500': urgency === 'high'
       }">
    <div class="p-5 flex-1">
      <div class="flex justify-between items-start mb-2">
        <h3 class="font-semibold text-lg">{{ title }}</h3>
        <span class="text-xs px-2 py-1 rounded"
              :class="{
                'bg-green-100 text-green-800': urgency === 'low',
                'bg-yellow-100 text-yellow-800': urgency === 'medium',
                'bg-red-100 text-red-800': urgency === 'high'
              }">
          {{ urgency.toUpperCase() }}
        </span>
      </div>
      
      <p class="text-gray-600 text-sm mb-4 line-clamp-3">{{ content }}</p>
      
      <div class="flex flex-wrap gap-1 mb-4">
        <span v-for="(tag, index) in tags" :key="index"
              class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
          {{ tag }}
        </span>
      </div>
    </div>
    
    <div class="bg-gray-50 px-5 py-3 border-t border-gray-200">
      <div class="flex justify-between items-center text-xs text-gray-500">
        <span>{{ author }}</span>
        <span>{{ formattedDate }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  title: String,
  content: String,
  author: String,
  date: String,
  urgency: {
    type: String,
    default: 'low',
    validator: value => ['low', 'medium', 'high'].includes(value)
  },
  tags: Array
});

const formattedDate = computed(() => {
  if (!props.date) return '';
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(props.date).toLocaleDateString(undefined, options);
});
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>