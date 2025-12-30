<template>
  <div>
    <h2 class="text-2xl font-bold mb-4">Predict Pest/Disease</h2>

    <div v-if="!isSettingsComplete" class="p-4 bg-yellow-100 text-yellow-700 rounded mb-4">
      <p>Please complete your farm settings to get personalized pest predictions.</p>
      <router-link to="/farmer-dashboard/farm-settings" class="mt-2 block text-blue-500 hover:text-blue-700">
        Go to Farm Settings
      </router-link>
    </div>

    <div v-else>
      <form @submit.prevent="predictPest" class="max-w-md mx-auto">
        <label class="block mb-2">
          Crop:
          <select v-model="crop" class="w-full p-2 border rounded">
            <option value="maize">Maize</option>
            <option value="wheat">Wheat</option>
            <option value="rice">Rice</option>
          </select>
        </label>

        <label class="block mb-2">
          Location:
          <select v-model="location" class="w-full p-2 border rounded">
            <option v-for="(weather, loc) in weatherData" :key="loc" :value="loc">{{ loc }}</option>
          </select>
        </label>

        <label class="block mb-2">
          Temperature (°C):
          <input v-model="temperature" type="number" class="w-full p-2 border rounded" placeholder="Enter temperature" />
        </label>

        <label class="block mb-2">
          Humidity (%):
          <input v-model="humidity" type="number" class="w-full p-2 border rounded" placeholder="Enter humidity" />
        </label>

        <label class="block mb-2">
          Rainfall (mm):
          <input v-model="rainfall" type="number" class="w-full p-2 border rounded" placeholder="Enter rainfall" />
        </label>

        <label class="block mb-2">
          Wind Speed (km/h):
          <input v-model="wind_speed" type="number" class="w-full p-2 border rounded" placeholder="Enter wind speed" />
        </label>

        <button type="submit" class="w-full bg-green-500 text-white p-2 rounded hover:bg-green-600">
          Predict Pest/Disease
        </button>
      </form>

      <div v-if="predictionResult" class="mt-4 p-4 bg-gray-100 rounded">
        <h3 class="text-xl font-bold">Prediction Result for {{ predictionResult.crop }}</h3>
        <ul>
          <li v-for="(value, pest) in predictionResult.result" :key="pest" class="mb-2">
            <span class="font-semibold">{{ pest }}:</span> {{ value }}
          </li>
        </ul>
      </div>

      <div v-if="error" class="mt-4 p-4 bg-red-100 text-red-700 rounded">
        <p>{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import apiClient from '@/api'; // Import your Axios instance
import { useRouter } from 'vue-router';

const router = useRouter();
const crop = ref('maize');
const location = ref('');
const temperature = ref('');
const humidity = ref('');
const rainfall = ref('');
const wind_speed = ref('');
const predictionResult = ref(null);
const error = ref('');
const isSettingsComplete = ref(false);

// Mock weather data
const weatherData = {
  "Nairobi": {"temperature": 25, "humidity": 70, "rainfall": 120, "wind_speed": 10},
  "Taita Hills": {"temperature": 22, "humidity": 75, "rainfall": 200, "wind_speed": 8},
  "Kisumu": {"temperature": 28, "humidity": 80, "rainfall": 180, "wind_speed": 12},
  "Mombasa": {"temperature": 30, "humidity": 85, "rainfall": 220, "wind_speed": 15},
};

// Fetch farm settings on component mount
onMounted(async () => {
  try {
    const response = await apiClient.get('/farm-settings');
    if (response.data.crop && response.data.location) {
      crop.value = response.data.crop;
      location.value = response.data.location;
      isSettingsComplete.value = true;

      // Pre-fill weather data based on location
      const weather = weatherData[location.value];
      if (weather) {
        temperature.value = weather.temperature;
        humidity.value = weather.humidity;
        rainfall.value = weather.rainfall;
        wind_speed.value = weather.wind_speed;
      }
    }
  } catch (err) {
    console.error('Error fetching farm settings:', err.response?.data || err.message);
  }
});

const predictPest = async () => {
  error.value = ''; // Reset error message
  predictionResult.value = null; // Reset prediction result

  try {
    const response = await apiClient.post('/predict_crop', {
      crop: crop.value,
      temperature: temperature.value,
      humidity: humidity.value,
      rainfall: rainfall.value,
      wind_speed: wind_speed.value,
    });

    // Handle the response
    predictionResult.value = response.data;
  } catch (err) {
    console.error('Error predicting pest:', err.response?.data || err.message);
    error.value = "Failed to fetch pest prediction. Please try again.";
  }
};
</script>

<style scoped>
/* Optional Tailwind CSS */
</style>