<template>
  <div>
    <nav class="bg-gray-800 p-4">
      <div class="container mx-auto flex justify-between items-center">
        <router-link to="/" class="text-white text-xl font-bold">Pest Alert System</router-link>
        <div class="space-x-4">
          <router-link to="/farmer-dashboard" class="text-white hover:text-green-400">Farmer Dashboard</router-link>
          <router-link to="/admin-dashboard" class="text-white hover:text-green-400">Admin Dashboard</router-link>
        </div>
      </div>
    </nav>

    <main class="container mx-auto p-4">
      <slot></slot> <!-- Farmer or Admin dashboard content will go here -->
    </main>

    <footer class="bg-gray-800 text-white text-center p-4 mt-8">
      <p>&copy; 2023 Pest Alert System. All rights reserved.</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'Base',
};
</script>

<style scoped>
/* Optional Tailwind CSS */
</style>