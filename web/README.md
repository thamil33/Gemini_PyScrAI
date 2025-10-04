# ScrAI Web UI

Web interface for ScrAI simulation control and management.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Zustand** - Lightweight state management

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development

Start the development server (requires API server running on port 8000):

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Architecture

### Project Structure

```
src/
├── components/          # React components
│   ├── DashboardLayout.tsx
│   ├── SimulationList.tsx
│   ├── ActiveSimulationPanel.tsx
│   └── CreateSimulationForm.tsx
├── services/           # API client
│   └── api.ts
├── stores/            # Zustand state management
│   └── simulationStore.ts
├── types/             # TypeScript definitions
│   └── api.ts
├── App.tsx            # Root component
├── main.tsx           # Entry point
└── index.css          # Global styles
```

### Features

- **Real-time Updates**: Automatic polling every 3 seconds
- **Simulation Management**: Create, start, and control simulations
- **Phase Control**: Advance simulations through their lifecycle phases
- **Status Monitoring**: View pending actions, events, and current phase
- **Responsive Design**: Works on desktop and mobile

### API Integration

The frontend proxies `/api` requests to the FastAPI backend at `http://localhost:8000`. This is configured in `vite.config.ts`.

### State Management

The app uses Zustand for global state:

- `simulations`: List of all simulations
- `activeSimulation`: Currently selected simulation
- `isFetching`: Loading state
- `error`: Error messages
- `connection`: Connection status (polling/sse/offline)

### Styling

Tailwind CSS provides utility classes with a custom theme for simulation-specific colors:

- **Phase colors**: Each simulation phase has a distinct color
- **Status colors**: Visual indicators for simulation status
- **Dark mode**: Full dark mode support

## Development Notes

### Running Locally

1. Ensure the FastAPI backend is running:
   ```bash
   python run_api.py
   ```

2. Start the frontend dev server:
   ```bash
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

### API Endpoints Used

- `GET /api/simulations` - List all simulations
- `POST /api/simulations` - Create new simulation
- `GET /api/simulations/{id}` - Get simulation details
- `POST /api/simulations/{id}/start` - Start simulation
- `POST /api/simulations/{id}/advance` - Advance phase

## Future Enhancements (Phase 2+)

- Server-Sent Events (SSE) for real-time updates
- Action composition interface
- Event management panel
- Map visualization with Leaflet
- Phase log viewer
- Dark mode toggle
