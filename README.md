## ScrAI Web UI - Quick Start Guide

# 🚀 ScrAI Web Interface

Modern web dashboard for controlling ScrAI simulations with real-time updates, phase management, and LLM integration.

## ✅ Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** and npm

## 🛠️ Quick Setup (2 minutes)

### 1. Install Python Dependencies
```bash
pip install -e .
```

### 2. Install Node Dependencies
```bash
cd web && npm install
```

### 3. Start Both Servers

**Terminal 1 - Backend API:**
```bash
python run_api.py
# Server runs on http://localhost:8000
```

**Terminal 2 - Frontend UI:**
```bash
cd web && npm run dev
# UI runs on http://localhost:3000
```

## 🎯 Usage

1. **Open** `http://localhost:3000` in your browser
2. **Create** a new simulation using the form
3. **Start** the simulation and watch real-time updates
4. **Inject actions** using the Action Composer
5. **Advance phases** to see the simulation progress

## 🔧 Key Features

- **Real-time Updates**: Live simulation status via SSE + polling fallback
- **Phase Control**: Start, advance, and monitor simulation phases
- **Action Injection**: Submit intents with LLM validation
- **Status Dashboard**: View pending actions, events, and actor states
- **Responsive Design**: Works on desktop and mobile

## 🛑 Stop Servers

- **Backend**: `Ctrl+C` in Terminal 1
- **Frontend**: `Ctrl+C` in Terminal 2

## 🔍 Troubleshooting

**"Module not found" errors?**
```bash
pip install -e .  # Install Python dependencies
cd web && npm install  # Install Node dependencies
```

**Port conflicts?**
- Backend uses port 8008
- Frontend uses port 3000
- Change ports in `run_api.py` and `web/vite.config.ts` if needed

**API connection issues?**
- Ensure backend is running first
- Check browser console for errors
- Verify `/api` requests are proxying correctly

## 📁 Project Structure

```
web/
├── src/components/     # React UI components
├── src/stores/        # State management (Zustand)
├── src/services/      # API client
└── src/types/         # TypeScript definitions
```

Ready to use! The UI provides a complete interface for simulation management with all Phase 2 features implemented.
