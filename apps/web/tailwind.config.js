/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        discord: {
          dark: "#36393f",
          darker: "#2f3136",
          darkest: "#202225",
          blurple: "#5865f2",
          green: "#3ba55c",
          red: "#ed4245",
          yellow: "#faa61a",
        },
      },
    },
  },
  plugins: [],
};
