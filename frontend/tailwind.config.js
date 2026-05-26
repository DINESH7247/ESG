/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          50: '#f6f7fb',
          100: '#eceff7',
          200: '#d5dcec',
          300: '#b0bdd8',
          400: '#8195bf',
          500: '#5f739d',
          600: '#46567c',
          700: '#323d5b',
          800: '#1f273f',
          900: '#121829',
        },
        mint: '#7dd3a7',
        sand: '#f3d6a3',
        rose: '#ef8fa7',
      },
      boxShadow: {
        soft: '0 20px 60px rgba(15, 23, 42, 0.12)',
      },
      backgroundImage: {
        'dashboard-grid': 'radial-gradient(circle at 1px 1px, rgba(255,255,255,0.12) 1px, transparent 0)',
      },
      fontFamily: {
        sans: ['"Space Grotesk"', '"IBM Plex Sans"', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
