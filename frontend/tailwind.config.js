/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        blue: {
          DEFAULT: "#1a3c6e",
          50:  "#eef2f9",
          100: "#d5e0f0",
          200: "#adc2e0",
          300: "#7a9dcc",
          400: "#4d7ab8",
          500: "#2d5fa3",
          600: "#1a3c6e",
          700: "#132d54",
          800: "#0d1f3b",
          900: "#061223",
        },
        green: {
          DEFAULT: "#2ea043",
          50:  "#edf8f0",
          100: "#ccedda",
          200: "#99dab5",
          300: "#5ec484",
          400: "#2ea043",
          500: "#268a38",
          600: "#1e722e",
          700: "#155924",
          800: "#0d401a",
          900: "#06270f",
        },
        brand: {
          blue: "#1a3c6e",
          green: "#2ea043",
          bg: "#f4f5f7",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease forwards",
        "slide-up": "slideUp 0.4s ease forwards",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};
