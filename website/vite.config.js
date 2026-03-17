import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ command }) => ({
  plugins: [react()],
  root: '.',
  // GitHub Pages project site is served from /yellow-pages/, not domain root.
  base: command === 'build' ? '/yellow-pages/' : '/',
}))
