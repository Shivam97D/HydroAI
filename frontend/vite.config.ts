import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/predict':     'http://localhost:8000',
      '/health':      'http://localhost:8000',
      '/history':     'http://localhost:8000',
      '/maps':        'http://localhost:8000',
      '/hydrograph':  'http://localhost:8000',
      '/metrics':     'http://localhost:8000',
      '/auth':        'http://localhost:8000',
      '/subscribers': 'http://localhost:8000',
      '/site-config': 'http://localhost:8000',
    },
  },
})
