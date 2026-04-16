import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: false,
    proxy: {
      '/analyze':   'http://localhost:5000',
      '/upload':    'http://localhost:5000',
      '/search':    'http://localhost:5000',
      '/diagnosis': 'http://localhost:5000',
      '/research':  'http://localhost:5000',
      '/health':    'http://localhost:5000',
      '/api':       'http://localhost:5000',
      '/cleanup':   'http://localhost:5000',
      '/database':  'http://localhost:5000',
      '/auth':      'http://localhost:5000',
    },
  },
})
