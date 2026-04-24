/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0D6E3B",
          50: "#E8F5EE",
          100: "#C3E4D0",
          500: "#0D6E3B",
          600: "#0A5A30",
          700: "#084525",
        },
        secondary: {
          DEFAULT: "#F5A623",
          50: "#FEF6E6",
          100: "#FDEAC0",
          500: "#F5A623",
          600: "#D48A0F",
        },
        danger: {
          DEFAULT: "#D63031",
          500: "#D63031",
          600: "#B52829",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
