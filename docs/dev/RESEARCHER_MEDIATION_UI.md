# Consolidated Dashboard - Researcher Mediation UI

## Overview

The ScrAI interface has been completely redesigned to implement the **Researcher Mediation UI** blueprint with a professional, streamlined workspace. The interface now features:

- **Single-Page Dashboard** when simulation is active
- **3 View Modes**: Workspace (mediation), Map (coming soon), Data (analytics)
- **Integrated Controls** with all functionality in one cohesive interface
- **Researcher-Focused Design** for reviewing and mediating LLM-generated content

## 🎛️ View Modes

### 1. Workspace Mode (Researcher Mediation)

**Purpose**: Primary interface for researchers to review, mediate, and inject content into simulations.

**Layout**: 3-column responsive grid
```
┌────────────────────────────────────────────┬─────────────────┐
│  🔍 Event Review & Mediation              │ ✍️ Inject Action│
│  (LLM-generated events for review)         │ (Manual/Player) │
│                                             │                 │
├────────────────────────────────────────────┤ 👥 Active       │
│  ⚙️ Action Queue & Resolution              │    Actors       │
│  (Pending actions + outcomes)              │ (Quick view)    │
│                                             │                 │
├────────────────────────────────────────────┴─────────────────┤
│  📝 Phase Logs (Execution history)                          │
└──────────────────────────────────────────────────────────────┘
```

**Features**:
- **Event Mediation**: Review LLM-generated events before they affect simulation
  - Color-coded by type (social, environmental, economic, political, system)
  - Status badges (pending, confirmed, resolved, cancelled)
  - Affected actors and locations displayed
  - Edit capabilities (future enhancement)

- **Action Mediation**: Monitor action queue and outcomes
  - Priority-based visual indicators (urgent → low)
  - Type icons for quick identification
  - Outcome display after resolution phase
  - LLM-parsed options visible

- **Action Composer**: Inject actions manually
  - Quick actor selection buttons
  - Simple intent/description fields
  - Optimized for researcher workflow

- **Actors Quick View**: Essential actor info at a glance
  - Location, traits, skills, role
  - Inline editing capabilities
  - Real-time attribute updates

### 2. Map Mode (Placeholder)

**Purpose**: Spatial visualization of simulation state.

**Planned Features**:
- Interactive map with OpenStreetMap tiles
- Actor markers with popups
- Event location indicators
- Custom overlays for scenario regions
- Visibility rules based on researcher permissions
- Real-time updates as simulation progresses

**Status**: UI placeholder ready, Leaflet.js integration pending

### 3. Data Mode (Analytics)

**Purpose**: Comprehensive data tables and detailed analytics.

**Tabs**:
- **Overview**: Simulation details, phase history, recent activity
- **Events**: Full event list with all metadata
- **Actions**: Complete action queue with resolution details
- **Actors**: Full actor management with CRUD operations
- **Logs**: Detailed phase execution logs

**Use Cases**:
- Deep dive into simulation data
- Export-ready views (future)
- Debugging and analysis
- Audit trail review

## 🎮 Control Bar

Located at the top of every view mode, providing:

**Left Section**:
- ← Back button (returns to simulation list)
- Simulation name and scenario
- Status indicator

**Right Section**:
- View mode switcher (🎛️ Workspace | 🗺️ Map | 📊 Data)

**Metrics Row**:
- Current Phase card (with cycle number)
- Quick metrics: Actors, Events, Actions counts
- Control buttons: ▶️ Start / ⏭️ Advance

## 🔄 Workflow

### Typical Researcher Session

1. **Select Simulation** from list or create new
2. **Start Simulation** (if newly created)
3. **Workspace Mode** opens automatically
4. **Review Events** in mediation panel
   - LLM has generated initial scenario events
   - Review descriptions and effects
   - Confirm or edit (future) before advancing
5. **Inject Actions** via composer
   - Select actor from quick buttons
   - Describe intended action
   - Submit to queue
6. **Advance Phase** to progress simulation
7. **Review Action Outcomes** after resolution
   - Check LLM-generated outcomes
   - Verify actor attribute changes
8. **Monitor Actors** for trait/skill evolution
9. **Check Phase Logs** for detailed notes
10. **Switch to Data Mode** for analytics
11. **Repeat cycle** for ongoing simulation

### LLM Integration Points

**Event Generation Phase**:
- Workspace shows newly generated events in mediation panel
- Researcher reviews before confirmation
- Can edit descriptions/effects (future enhancement)

**Action Resolution Phase**:
- Workspace displays resolved actions with outcomes
- LLM-generated results shown in outcome panel
- Consequence events appear in event mediation panel

**World Update Phase**:
- Actor attributes update in real-time
- Changes visible in Actors Quick View
- Trait/skill modifications highlighted

## 🎨 Design Philosophy

### Principles

1. **Mediation First**: Researchers review LLM output before it affects simulation
2. **Context at a Glance**: Key metrics always visible in control bar
3. **Minimize Clicks**: All essential functions in one workspace
4. **Progressive Disclosure**: Details expand on demand
5. **Mobile-Friendly**: Responsive grid adapts to screen size

### Visual Hierarchy

**Primary**: Event/Action mediation panels (largest, center-left)
**Secondary**: Action composer and actor view (right sidebar)
**Tertiary**: Phase logs (bottom, collapsible)
**Persistent**: Control bar with metrics (top, always visible)

### Color Coding

All components use consistent color language:
- **Blue**: Primary actions, normal priority, confirmed states
- **Purple**: Events, event generation phase
- **Orange**: Actions, high priority, action resolution phase
- **Green**: Success, resolved, running status
- **Yellow**: Pending, warnings
- **Red**: Urgent, errors, cancelled
- **Gray**: System, low priority, neutral

## 🚀 Future Enhancements

### Event Editing
- Inline editing of LLM-generated event descriptions
- Effect modification before confirmation
- Researcher notes/annotations

### Action Parsing
- Visual display of LLM-parsed action options
- Manual override of parsing results
- Batch action injection

### Map Integration
- Leaflet.js-based interactive map
- Actor/event location visualization
- Click-to-inject actions on map
- Spatial relationship visualization

### Real-time Collaboration
- WebSocket-based live updates
- Multi-researcher sessions
- Activity feed of researcher actions
- Conflict resolution for concurrent edits

### Analytics & Export
- Timeline visualization
- Event/action causality graphs
- Actor relationship networks
- Export simulation as narrative text
- CSV/JSON data exports

### NPC Autonomy
- Zeus Mode visibility of NPC-generated actions
- Approve/reject NPC intents
- Override NPC decision-making
- NPC behavior tuning

## 📊 Technical Implementation

### State Management
- Zustand store (`useSimulationStore`) manages simulation state
- Polling every 2 seconds for updates (will migrate to WebSocket)
- Optimistic UI updates for actions

### Component Architecture
```
SimulationDashboard (main container)
├── Top Control Bar
│   ├── Navigation (back button)
│   ├── View mode switcher
│   ├── Metrics cards
│   └── Phase controls
├── WorkspaceView (mediation interface)
│   ├── EventViewer (with mediation context)
│   ├── ActionViewer (with outcome display)
│   ├── ActionComposer (compact form)
│   ├── ActorManager (quick view)
│   └── PhaseLogViewer (collapsible)
├── MapView (placeholder)
│   └── Leaflet.js integration (pending)
└── DataView (analytics)
    └── Tabbed interface (overview, events, actions, actors, logs)
```

### Responsive Breakpoints
- **Mobile** (< 768px): Single column, stacked panels
- **Tablet** (768px - 1024px): 2-column workspace
- **Desktop** (> 1024px): 3-column workspace with full sidebar

## 📝 Usage Examples

### Starting a New Simulation
```
1. No active simulation → Shows "Create Simulation" form
2. Enter name: "My Town Experiment"
3. Select scenario: "simple_town"
4. Click "Create"
5. Dashboard opens in Workspace mode
6. Click "▶️ Start" in control bar
7. Scenario seeds with actors and events
8. Review events in mediation panel
```

### Injecting Player Actions
```
1. In Workspace mode, locate "✍️ Inject Action" panel
2. Click actor quick-select button (e.g., "Sarah the Teacher")
3. Enter intent: "Organize a community meeting to discuss water shortage"
4. (Optional) Add description for researchers
5. Click "📤 Submit Action"
6. Action appears in "⚙️ Action Queue & Resolution" panel
7. Advance to ACTION_RESOLUTION phase
8. Review LLM-generated outcome in action card
```

### Reviewing LLM Content
```
1. Advance to EVENT_GENERATION phase
2. New events appear in "🔍 Event Review & Mediation"
3. Read event descriptions (LLM-generated narratives)
4. Check affected actors and locations
5. Verify event type and status
6. (Future) Edit if needed before confirmation
7. Advance to next phase to apply events
```

### Analyzing Simulation
```
1. Click "📊 Data" in view mode switcher
2. Review "Overview" tab for simulation details
3. Switch to "Events" tab for full event history
4. Review "Actions" tab for complete action log
5. Check "Actors" tab for attribute analysis
6. Read "Logs" tab for detailed phase notes
7. Return to "🎛️ Workspace" for continued mediation
```

## ✅ Completion Status

- [x] Consolidated dashboard layout
- [x] Workspace mode with mediation panels
- [x] Integrated action composer
- [x] Actors quick view
- [x] Event/action mediation UI
- [x] Data mode with analytics tabs
- [x] Map mode placeholder
- [x] Responsive design
- [x] Dark mode support
- [x] Control bar with metrics
- [ ] Event editing capabilities
- [ ] Map view with Leaflet.js
- [ ] WebSocket real-time updates
- [ ] Export functionality
- [ ] Multi-researcher support

**Status**: ✅ Researcher Mediation UI - MVP Complete and Ready for Testing
