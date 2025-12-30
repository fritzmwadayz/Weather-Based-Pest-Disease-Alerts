import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
//import flowbite from '@flowbite/plugin';

export default defineConfig({
    content: ['./index.html', 
    './src/**/*.{vue,js,ts,jsx,tsx}',
    //'./node_modules/flowbite/**/*.js'
  ],
  theme: { 
    extend: {
      borderRadius: {
        'lg': '0.5rem', // ensures rounded-lg is available
      }
    } 
  },
  plugins: [
    vue(),
    tailwindcss(),
    //flowbite()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@tests': path.resolve(__dirname, './tests')
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        ws: true // for websocket
      }
    }
  }
});