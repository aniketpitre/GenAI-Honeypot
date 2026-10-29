import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    // `npm run dev` talks to a locally running API
    proxy: { '/api': process.env.VITE_DEV_API ?? 'http://localhost:8080' },
  },
});
