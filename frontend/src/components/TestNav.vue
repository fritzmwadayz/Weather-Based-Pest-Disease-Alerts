<template>
  <!-- Fixed Top Bar -->
  <nav class="bg-white border-gray-200 dark:bg-gray-900 fixed w-full top-0 z-50">
    <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
      <!-- Logo and Sidebar Toggle Button -->
      <div class="flex items-center space-x-3 rtl:space-x-reverse">
        <!-- Sidebar Toggle Button -->
        <button
          @click="toggleSidebar"
          type="button"
          class="inline-flex items-center p-2 w-10 h-10 justify-center text-sm text-gray-500 rounded-lg md:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
        >
          <span class="sr-only">Toggle sidebar</span>
          <svg
            class="w-5 h-5"
            aria-hidden="true"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 17 14"
          >
            <path
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M1 1h15M1 7h15M1 13h15"
            />
          </svg>
        </button>

        <!-- Logo -->
        <a href="localhost:5173/farmer-dashboard" class="flex items-center space-x-3 rtl:space-x-reverse">
          <span class="self-center text-2xl font-semibold whitespace-nowrap dark:text-white">GreenShield</span>
        </a>
      </div>

      <!-- User Dropdown -->
      <div class="flex items-center md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
        <!-- User Dropdown Button -->
        <button
          @click="toggleDropdown"
          type="button"
          class="flex text-sm bg-gray-800 rounded-full md:me-0 focus:ring-4 focus:ring-gray-300 dark:focus:ring-gray-600"
          id="user-menu-button"
          aria-expanded="false"
        >
          <span class="sr-only">Open user menu</span>
          <!--<img
            class="w-8 h-8 rounded-full"
            :src="userProfileImage"
            alt="User photo"
          />-->
          <img class="w-8 h-8 rounded-full" src="/home/mwadayz/Mwadayz/Pictures/Profiles/profile.jpg" alt="user photo">
        </button>

        <!-- Dropdown Menu -->
        <div
          v-if="isDropdownOpen"
          class="z-50 absolute right-4 mt-12 text-base list-none bg-white divide-y divide-gray-100 rounded-lg shadow-sm dark:bg-gray-700 dark:divide-gray-600"
          id="user-dropdown"
        >
          <div class="px-4 py-3">
            <span class="block text-sm text-gray-900 dark:text-white">{{ userName }}</span>
            <span class="block text-sm text-gray-500 truncate dark:text-gray-400">{{ userEmail }}</span>
          </div>
          <ul class="py-2" aria-labelledby="user-menu-button">
            <li>
              <router-link
                to="/farmer-dashboard"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white"
              >
                Dashboard
              </router-link>
            </li>
            <li>
              <router-link
                to="/farmer-dashboard/general-settings"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white"
              >
                Settings
              </router-link>
            </li>
            <li>
              <router-link
                to="/farmer-dashboard/farm-settings"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white"
              >
                Farm
              </router-link>
            </li>
            <li>
              <a
                @click="logout"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white cursor-pointer"
              >
                Sign out
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>

  <!-- Main Content (with padding to account for fixed navbar) -->
  <div class="pt-16">
    <!-- Your main content goes here -->
    <p>Main content goes here...</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

// Reactive state for dropdown and sidebar
const isDropdownOpen = ref(false);

// User data (replace with dynamic data from your app)
const userName = ref("test");
const userEmail = ref("test@test.com");
const userProfileImage = ref("/home/mwadayz/Mwadayz/Pictures/Profiles/profile.jpg");

// Toggle dropdown
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value;
};

// Toggle sidebar (you can implement this logic in your parent component)
const toggleSidebar = () => {
  console.log("Sidebar toggled");
  // Emit an event or update a store to toggle the sidebar
};

// Logout function
const router = useRouter();
const logout = () => {
  // Add your logout logic here
  console.log("User logged out");
  // Example: Clear user session and redirect to login page
  localStorage.removeItem("token");
  router.push("/login");
};
</script>

<style scoped>
/* Ensure the dropdown is positioned correctly */
#user-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
}
</style>