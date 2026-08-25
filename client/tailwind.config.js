/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        jarvis: {
          bg: "#050B14",
          card: "rgba(10, 25, 47, 0.75)",
          border: "rgba(0, 240, 255, 0.25)",
          glow: "#00f0ff",
          cyan: "#00e5ff",
          amber: "#ffaa00",
          danger: "#ff3366",
          emerald: "#00ff9d",
          blue: "#0070f3"
        }
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', '"Fira Code"', 'Consolas', 'monospace'],
        orbitron: ['"Orbitron"', 'sans-serif'],
      },
      boxShadow: {
        'neon-cyan': '0 0 15px rgba(0, 240, 255, 0.4), 0 0 30px rgba(0, 240, 255, 0.2)',
        'neon-amber': '0 0 15px rgba(255, 170, 0, 0.4), 0 0 30px rgba(255, 170, 0, 0.2)',
        'neon-danger': '0 0 20px rgba(255, 51, 102, 0.5), 0 0 40px rgba(255, 51, 102, 0.3)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 12s linear infinite',
        'spin-reverse': 'spin-reverse 16s linear infinite',
        'scanline': 'scanline 8s linear infinite',
      },
      keyframes: {
        'spin-reverse': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(-360deg)' }
        },
        'scanline': {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        }
      }
    },
  },
  plugins: [],
}
