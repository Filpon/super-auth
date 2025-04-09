import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  server: {
    cors: true, // For development server
    proxy: {
      '/api': {
        target: `${import.meta.env.REACT_APP_BACKEND_URL}:${import.meta.env.BACKEND_PORT}`,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
    headers: {
      'Access-Control-Allow-Origin': '*',
    },
  },
  plugins: [react()],
});
