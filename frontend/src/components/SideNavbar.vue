<template>
  <nav
    class="bg-gray-800 text-white min-h-screen p-4 fixed top-16 left-0 z-40 transition-all duration-300"
    :style="{ width: sidebarWidth }"
  >
    <div class="space-y-4">
      <!-- Collapse Icon -->
      <span
        class="collapse-icon block p-2 hover:bg-gray-700 rounded cursor-pointer"
        :class="{ 'rotate-180': collapsed }"
        @click="toggleSidebar"
      >
        <i class="fas fa-angle-double-left"></i>
      </span>

      <!-- Dashboard -->
      <SideBarLinks to="/farmer-dashboard" icon="fa-home">Dashboard</SideBarLinks>

      <!-- Pest Prediction -->
      <SideBarLinks to="/farmer-dashboard/predict_crop" icon="fa-bug">Pest Prediction</SideBarLinks>

      <!-- Farm Settings -->
      <SideBarLinks to="/farmer-dashboard/farm-settings" icon="fa-tractor">Farm Settings</SideBarLinks>

      <!-- General Settings -->
      <SideBarLinks to="/farmer-dashboard/general-settings" icon="fa-cog">General Settings</SideBarLinks>

      <!-- Reports (Optional) -->
      <SideBarLinks to="/reports" icon="fa-chart-line">Reports</SideBarLinks>

      <!-- Help/Support -->
      <SideBarLinks to="/help" icon="fa-question-circle">Help/Support</SideBarLinks>

      <!-- Logout -->
      <button @click="logout" class="w-full text-left p-2 hover:bg-gray-700 rounded">
        <i class="fas fa-sign-out-alt mr-2"></i>
        Logout
      </button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { ref, computed } from 'vue';
import SideBarLinks from '@/components/SideBar/SideBarLinks.vue'; // Adjust the path as needed

// Sidebar state
const collapsed = ref(false);
const SIDEBAR_WIDTH = '16rem'; // Default width
const SIDEBAR_WIDTH_COLLAPSED = '4rem'; // Collapsed width

// Compute sidebar width based on collapsed state
const sidebarWidth = computed(() => {
  return collapsed.value ? SIDEBAR_WIDTH_COLLAPSED : SIDEBAR_WIDTH;
});

// Toggle sidebar collapse
const toggleSidebar = () => {
  collapsed.value = !collapsed.value;
};

// Logout function
const router = useRouter();
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  router.push('/login');
};
</script>

<style scoped>
/* Sidebar styling */
nav {
  background-color: #2d3748; /* bg-gray-800 */
  color: white;
  transition: width 0.3s ease;
}

/* Collapse icon styling */
.collapse-icon {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  padding: 0.5rem;
  color: white;
  transition: transform 0.2s linear;
}

.collapse-icon:hover {
  background-color: #4a5568; /* bg-gray-700 */
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>