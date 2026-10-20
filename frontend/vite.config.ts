import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// PWA/service worker is intentionally off. NAS clients were precaching the
// whole app and then main.tsx unregistered the worker, so the first visit
// downloaded everything twice.
export default defineConfig({
  plugins: [
    react(),
  ],
  server: {
    host: true,
    port: 3000,
    watch: {
      usePolling: true,
    },
  },
  preview: {
    host: true,
    port: 3000,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
