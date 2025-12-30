import { createApp } from 'vue'
import { createPinia } from 'pinia' // Import Pinia
import './style.css'
import '@/assets/main.css'
import App from './App.vue'
import router from '@/router/index.js'
import '@fortawesome/fontawesome-free/css/all.min.css'
import { initializeApp } from '@/services/init'

// Initialize app
const app = createApp(App)

// Create Pinia store instance
const pinia = createPinia()

// Register plugins
app.use(pinia)
app.use(router)

// Mount app
//app.mount('#app')

// Initialize before mounting
//initializeApp().then(() => {
  //app.mount('#app')
//})

initializeApp().finally(() => {
  app.mount('#app')
})