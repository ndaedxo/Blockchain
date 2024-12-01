/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './webapp/templates/**/*.html',  // Include all HTML templates
    './webapp/static/js/**/*.js',     // Include any JavaScript files that may use Tailwind classes
    // Add other paths as necessary
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

