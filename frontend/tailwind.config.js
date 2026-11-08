/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#14213D",
        paper: "#EEF1F6",
        teal: { 50: "#E6F6F3", 600: "#0E9F8E", 700: "#0B7F72" },
        amber: { 50: "#FDF3DC", 700: "#9A6400" },
      },
      fontFamily: {
        display: ['"Bricolage Grotesque"', "system-ui", "sans-serif"],
        sans: ['"Source Sans 3"', "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
