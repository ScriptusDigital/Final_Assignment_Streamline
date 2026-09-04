import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => ({
  plugins: [react()],

  base: (
    command === 'build'
      ? '/static/frontend/'
      : '/'
  ),

  build: {
    outDir: fileURLToPath(
      new URL(
        '../static/frontend',
        import.meta.url,
      ),
    ),
    emptyOutDir: true,
  },

server: {
  port: 5173,
  strictPort: true,

  proxy:  {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
}))