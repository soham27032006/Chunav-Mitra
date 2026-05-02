import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteTsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [
    tanstackStart({ server: { preset: 'node-server' } }),
    react(),
    viteTsConfigPaths()
  ],
  server: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
    allowedHosts: 'all'
  },
  preview: {
    host: '0.0.0.0',
    port: parseInt(process.env.PORT || '3000'),
    allowedHosts: 'all'
  },
})
