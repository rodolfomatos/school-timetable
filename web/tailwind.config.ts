/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@ilabuporto/design-system/dist/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: "#009FDF",
        accent: "#22c55e",
        destructive: "#ef4444",
        warning: "#eab308",
        info: "#3b82f6",
      },
    },
  },
  plugins: [],
}
