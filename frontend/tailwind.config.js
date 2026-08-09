/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#12203B",
          light: "#1B2E52",
          dark: "#0B1526",
        },
        paper: "#F7F5F0",
        amber: {
          DEFAULT: "#F5A623",
          dark: "#D98C0F",
        },
        cargo: {
          DEFAULT: "#0E7C7B",
          light: "#12A3A1",
        },
        slate2: "#5B6472",
        alert: "#D64545",
      },
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
