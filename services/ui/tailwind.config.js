/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './**/*.{ts,tsx}', '!./node_modules/**'],
  theme: {
    extend: {
      colors: {
        'sentinel-blue': '#0D1B2A',
        'sentinel-navy': '#1B263B',
        'sentinel-steel': '#415A77',
        'sentinel-silver': '#778DA9',
        'sentinel-light': '#E0E1DD',
        'sentinel-cyan': '#00F5D4',
        'sentinel-red': '#FF4747',
      },
      fontFamily: { sans: ['Inter', 'sans-serif'], mono: ['Fira Code', 'monospace'] },
    },
  },
  plugins: [],
};
