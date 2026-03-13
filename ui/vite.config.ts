import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

const apiHost = process.env.API_HOST || 'localhost:8000'
// Ensure the proxy target has a protocol (Vite requires it).
const proxyTarget = apiHost.startsWith('http://') || apiHost.startsWith('https://')
  ? apiHost
  : `http://${apiHost}`

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // Keep the same /api path used in production (Nginx proxy).
      // Strip the /api prefix because the backend routes do not include it.
      '/api': {
        target: proxyTarget,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})