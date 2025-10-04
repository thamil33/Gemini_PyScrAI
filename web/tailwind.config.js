/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Simulation-specific colors
        phase: {
          initialize: '#3B82F6',    // blue
          event_generation: '#8B5CF6',     // violet
          action_collection: '#F59E0B', // amber
          action_resolution: '#EF4444',  // red
          world_update: '#10B981',    // emerald
          snapshot: '#06B6D4',        // cyan
        },
        // Status colors
        status: {
          created: '#6B7280',
          running: '#10B981',
          paused: '#F59E0B',
          completed: '#3B82F6',
          error: '#EF4444',
        }
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
