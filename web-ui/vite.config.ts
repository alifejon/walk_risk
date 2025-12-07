import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // Code splitting for better caching
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['framer-motion', 'recharts'],
          'data-vendor': ['axios', '@tanstack/react-query', 'zustand'],
        },
      },
    },
    // Reduce chunk size warning threshold
    chunkSizeWarningLimit: 600,
    // Enable source maps for debugging
    sourcemap: false,
  },
  // Preview server config (for local production testing)
  preview: {
    port: 3000,
  },
  // Dev server config
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
