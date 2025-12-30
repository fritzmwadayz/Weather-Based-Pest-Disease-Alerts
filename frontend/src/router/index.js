import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Login from '@/views/Login.vue';
import FarmSettings from '@/views/FarmSettings.vue';
import GeneralSettings from '@/views/GeneralSettings.vue';
import Base from '@/views/Base.vue';
import AdminDashboard from '@/views/AdminDashboard.vue';
import FarmerDashboard from '@/views/FarmerDashboard.vue';
import ForgotPassword from '@/views/ForgotPassword.vue';
import Signup from '@/views/Signup.vue';
import ResetPassword from '@/views/ResetPassword.vue';
import BlogCard from '@/components/cards/BlogCard.vue';
import PredictPestDisease from '@/components/PredictPestDisease.vue';
import TestStores from '@/components/TestStores.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', redirect: '/login' },
  {
    path: '/home',
    component: Home,
    meta: { requiresAuth: false },
  },
  { path: '/login', component: Login },//
  {
    path: '/admin-dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/farmer-dashboard',
    component: FarmerDashboard,
    children: [
      {
        path: 'predict_crop',
        component: PredictPestDisease,
      },
      {
        path: 'farm-settings',
        component: FarmSettings,
      },
      {
        path: 'general-settings',
        component: GeneralSettings,
      },
    ],
    meta: { requiresAuth: true, role: 'farmer' },
  },
  {
    path: '/sign-up',
    component: Signup,
    meta: { requiresAuth: false },
  },
  {
    path: '/forgot-password',
    component: ForgotPassword,
    meta: { requiresAuth: false },
  },
  {
    path: '/reset-password',
    component: ResetPassword,
    meta: { requiresAuth: false },
  },
  {
  path: '/test-stores',
  component: TestStores
  },
];

//Router configuration
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // Always return a resolved promise
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(savedPosition || { top: 0 })
      }, 100)
    })
  }
})

//Navigation guard
/*router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const role = localStorage.getItem('role');
  const token = localStorage.getItem('token');
  console.log('Navigating from', from.path, 'to', to.path);
  console.log('Token:', token);
  console.log('Role:', role);

  if (to.meta.requiresAuth && !token) {
    console.log('Redirecting to login: User not authenticated');
    next('/login');
  } else if (to.meta.role && to.meta.role !== role) {
    console.log(`Redirecting to ${role === 'admin' ? 'admin' : 'farmer'} dashboard: Role mismatch`);
    next(role === 'admin' ? '/admin-dashboard' : '/farmer-dashboard');
  } else {
    console.log('Proceeding to route:', to.path);
    next();
  }
});*/

  router.beforeEach(async (to) => {
    const authStore = useAuthStore()
  
    // Wait for auth initialization if token exists
    if (authStore.token && !authStore.user) {
      try {
        await authStore.hydrateUser()
      } catch (err) {
        return '/login'
      }
    }

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
      return '/login'
    }

    if (to.meta.role && to.meta.role !== authStore.role) {
      return authStore.role === 'admin' 
        ? '/admin-dashboard' 
        : '/farmer-dashboard'
    }
  });

export default router;