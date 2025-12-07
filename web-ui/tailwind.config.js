/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'game-bg': '#0D0D1A',
        'game-card': '#1A1A2E',
        'game-border': '#16213E',
        'neon-cyan': '#00F5FF',
        'neon-pink': '#FF00FF',
        'neon-green': '#39FF14',
        'neon-yellow': '#FFE66D',
        'neon-red': '#FF3F3F',
        'neon-purple': '#9D00FF',
      },
      fontFamily: {
        korean: ['Noto Sans KR', 'sans-serif'],
      },
      boxShadow: {
        'neon': '0 0 5px #00F5FF, 0 0 20px #00F5FF',
        'neon-pink': '0 0 5px #FF00FF, 0 0 20px #FF00FF',
        'neon-green': '0 0 5px #39FF14, 0 0 20px #39FF14',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 5px #00F5FF' },
          '50%': { boxShadow: '0 0 20px #00F5FF, 0 0 30px #00F5FF' },
        },
      },
    },
  },
  plugins: [],
}
