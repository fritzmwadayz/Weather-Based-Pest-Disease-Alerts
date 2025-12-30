<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'; // Import useRouter
import { updateGeneralSettings } from '@/api';

const router = useRouter(); // Initialize the router
const generalSettings = ref({
  notifications: true,
  dark_mode: false,
});

/*
const fetchSettings = async () => {
  try {
    const response = await getGeneralSettings();
    generalSettings.value = response.data;
  } catch (error) {
    console.error('Error fetching general settings:', error);
  }
}; */

const saveSettings = async () => {
  try {
    await updateGeneralSettings(generalSettings.value);
    alert('Settings updated successfully!');
    router.push('/farmer-dashboard'); // Redirect to the farmer dashboard
  } catch (error) {
    console.error('Error updating settings:', error);
  }
};

onMounted(fetchSettings);

</script>

<template>
  <div class="p-6 max-w-lg mx-auto bg-white shadow-md rounded-md">
    <h2 class="text-2xl font-bold mb-4">General Settings</h2>

    <label class="flex items-center space-x-2">
      <input type="checkbox" v-model="generalSettings.notifications" class="form-checkbox">
      <span>Enable Notifications</span>
    </label>

    <label class="flex items-center space-x-2 mt-4">
      <input type="checkbox" v-model="generalSettings.dark_mode" class="form-checkbox">
      <span>Enable Dark Mode</span>
    </label>

    <button @click="saveSettings" class="mt-4 bg-green-500 text-white px-4 py-2 rounded">
      Save Changes
    </button>
  </div>
</template>