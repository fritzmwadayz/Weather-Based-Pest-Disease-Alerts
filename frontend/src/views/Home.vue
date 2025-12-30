<template>
  <div class="text-center">
    <h1 class="text-3xl font-bold mb-4">Welcome to the Pest & Disease Alert System</h1>
    <p class="mb-8">Protect your crops with real-time pest and disease predictions.</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
      <router-link to="/login" class="p-6 bg-green-100 rounded-lg shadow-md hover:bg-green-200 transition">
        <h2 class="text-xl font-semibold mb-2">Get Started</h2>
        <p>Get pest and disease predictions for your crops.</p>
      </router-link>
    </div>

    <div class="mt-8">
      <h2 class="text-2xl font-bold mb-4">About Us</h2>
      <p class="max-w-2xl mx-auto">
        Our mission is to help farmers protect their crops by providing accurate and timely pest and disease predictions.
      </p>
    </div>

  </div>
</template>

<script>
import { ref } from 'vue';
export default {
  name: 'Home',
};

</script>

<style scoped>
/* Optional Tailwind CSS */
</style>