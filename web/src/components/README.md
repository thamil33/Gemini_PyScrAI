# ScrAI UI Components

## Overview

The ScrAI frontend provides a comprehensive dashboard for managing and visualizing LLM-powered social simulations. The UI is built with React, TypeScript, and TailwindCSS, featuring real-time updates and rich data visualization.

## Component Architecture

### 🎯 SimulationDashboard (NEW)
**Path:** `SimulationDashboard.tsx`

The main dashboard component that integrates all simulation views into a tabbed interface.

**Features:**
- **Overview Tab**: 4 metric cards (Current Phase, Active Actors, Pending Events, Pending Actions), simulation details, phase history, recent activity preview
- **Events Tab**: Full EventViewer with color-coded event types
- **Actions Tab**: Complete ActionViewer with priority borders and outcomes
- **Actors Tab**: Integrated ActorManager with CRUD operations
- **Logs Tab**: Enhanced PhaseLogViewer with detailed phase execution logs

**Props:**
```typescript
interface SimulationDashboardProps {
  simulation: SimulationDetail;
}
```

**Usage:**
```tsx
<SimulationDashboard simulation={activeSimulation} />
```

### 📊 EventViewer (NEW)
**Path:** `EventViewer.tsx`

Displays simulation events with visual coding for types and statuses.

**Features:**
- **Color-Coded Event Types**:
  - 🔵 Social (blue-100): Interactions, relationships
  - 🟢 Environmental (green-100): Natural phenomena, weather
  - 🟡 Economic (yellow-100): Trade, markets, transactions
  - 🟣 Political (purple-100): Governance, elections
  - ⚫ System (gray-100): Meta-simulation events
  
- **Status Badges**:
  - 🟡 Pending: Event awaiting processing
  - 🔵 Confirmed: Event validated and active
  - 🟢 Resolved: Event completed
  - 🔴 Cancelled: Event invalidated

- **Rich Details**: Affected actors, location, source, trigger action, timestamps

**Props:**
```typescript
interface EventViewerProps {
  events: EventSummary[];
  actors?: Array<{ id: string; name: string }>;
}
```

### ⚙️ ActionViewer (NEW)
**Path:** `ActionViewer.tsx`

Visualizes actor actions with priority-based styling and outcome display.

**Features:**
- **Priority Border Colors**:
  - 🔴 Urgent (red-300): Critical actions requiring immediate resolution
  - 🟠 High (orange-300): Important actions
  - 🔵 Normal (blue-300): Standard priority
  - ⚫ Low (gray-300): Background tasks

- **Action Type Icons**:
  - 🚶 Movement: Location changes
  - 💬 Communication: Dialogue, messages
  - 🤝 Interaction: Social interactions
  - 💰 Economic: Trade, transactions
  - 👥 Social: Group activities
  - ⚔️ Combat: Conflicts
  - 🔬 Research: Investigation
  - 📋 Custom: Other actions

- **Outcome Display**: Shows LLM-generated action resolution results with success indicators

**Props:**
```typescript
interface ActionViewerProps {
  actions: ActionSummary[];
  actors?: Array<{ id: string; name: string }>;
}
```

### 📝 PhaseLogViewer (Enhanced)
**Path:** `PhaseLogViewer.tsx`

Enhanced to display detailed phase execution logs with icons and color coding.

**Features:**
- **Phase-Specific Colors**:
  - Initialize: Gray border
  - Event Generation: Purple border
  - Action Collection: Blue border
  - Action Resolution: Orange border
  - World Update: Green border
  - Snapshot: Cyan border

- **Phase Icons**:
  - 🚀 Initialize
  - ⚡ Event Generation
  - 📥 Action Collection
  - ⚙️ Action Resolution
  - 🌍 World Update
  - 📸 Snapshot

- **Expandable View**: Collapsible panel with scrollable log history
- **Detailed Notes**: Shows LLM-generated phase notes ("Generated 3 events via LLM", etc.)

**Props:**
```typescript
interface PhaseLogViewerProps {
  logs: PhaseLogEntry[];
  defaultExpanded?: boolean;
  maxHeight?: string; // Tailwind height class number (e.g., '96')
}
```

### 👥 ActorManager (Enhanced)
**Path:** `ActorManager.tsx`

Enhanced to display rich actor attributes with visual indicators.

**New Features:**
- **📍 Location Display**: Shows actor's current location (e.g., "Town Hall")
- **✨ Traits**: Key-value pairs (e.g., "leadership: high", "wisdom: 8")
- **🎯 Skills**: Array of capabilities (e.g., "teaching", "mentoring")
- **👤 Role**: Actor's role from metadata (e.g., "teacher", "trader")

**Props:**
```typescript
interface ActorManagerProps {
  simulationId: string;
}
```

## Type System

### Enums (Matching Backend)

All TypeScript enums in `types/api.ts` match the Python backend exactly:

```typescript
enum EventType {
  SOCIAL = 'social',
  ENVIRONMENTAL = 'environmental',
  ECONOMIC = 'economic',
  POLITICAL = 'political',
  SYSTEM = 'system',
}

enum EventStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  RESOLVED = 'resolved',
  CANCELLED = 'cancelled',
}

enum ActionType {
  MOVEMENT = 'movement',
  COMMUNICATION = 'communication',
  INTERACTION = 'interaction',
  ECONOMIC = 'economic',
  SOCIAL = 'social',
  COMBAT = 'combat',
  RESEARCH = 'research',
  CUSTOM = 'custom',
}

enum ActionStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

enum ActionPriority {
  URGENT = 'urgent',
  HIGH = 'high',
  NORMAL = 'normal',
  LOW = 'low',
}
```

### Enhanced Interfaces

**EventDetail:**
```typescript
interface EventDetail extends EventSummary {
  affected_actors: string[];        // Actor IDs affected by event
  location: Record<string, unknown> | null; // Event location
  source: string | null;             // Event origin/trigger
  trigger_action_id: string | null;  // Action that caused event
  effects: Record<string, unknown>;  // LLM-generated effects
  parameters: Record<string, unknown>; // Event parameters
  scope: string | null;              // Event scope (global, local, etc.)
  modifications: Record<string, unknown>; // State modifications
}
```

**ActionDetail:**
```typescript
interface ActionDetail extends ActionSummary {
  simulation_id: string;
  outcome: string | null;            // LLM-generated resolution result
  type: ActionType;
  generated_events: string[];        // IDs of events generated by action
  llm_parsed: boolean;               // Whether parsed by LLM
  parsed_options: Record<string, unknown>; // LLM-extracted options
}
```

## Data Flow

```
Backend LLM Phase Handlers
         ↓
   FastAPI Endpoints
         ↓
  Frontend API Client
         ↓
   Zustand Store (simulationStore)
         ↓
  React Components (Dashboard, EventViewer, etc.)
         ↓
    User Interface
```

## Integration Example

```tsx
import { SimulationDashboard } from './components/SimulationDashboard';
import { useSimulationStore } from './stores/simulationStore';

function App() {
  const { activeSimulation } = useSimulationStore();

  return (
    <div>
      {activeSimulation && (
        <SimulationDashboard simulation={activeSimulation} />
      )}
    </div>
  );
}
```

## Styling Guidelines

### Color Palette
- **Primary**: Blue (info, confirmed, normal priority)
- **Success**: Green (resolved, world updates)
- **Warning**: Yellow/Orange (pending, high priority, economic)
- **Danger**: Red (urgent, failed, cancelled)
- **Social**: Purple (political events, event generation)
- **Neutral**: Gray (system events, low priority)

### Component Structure
All components follow consistent structure:
1. **Header**: Title, counts, action buttons
2. **Content**: Main data display with color coding
3. **Details**: Expandable/collapsible additional info
4. **Footer**: Timestamps, metadata

### Responsive Design
- Mobile: Single column, stacked cards
- Tablet: 2-column grids
- Desktop: Multi-column with sidebar
- Dark Mode: Full support with `dark:` Tailwind classes

## LLM Integration Features

The UI is designed to showcase LLM-generated content:

1. **Event Narratives**: Display rich event descriptions generated by the LLM
2. **Action Outcomes**: Show detailed resolution results with success/failure indicators
3. **Actor Effects**: Visualize attribute changes (traits, skills) from LLM decisions
4. **Phase Notes**: Display LLM processing notes ("Generated X events", "Applied Y effects")
5. **World State Updates**: Show how events affect actors and the simulation world

## Testing

To test the new UI components:

1. Start the API server: `python run_api.py`
2. Start the frontend: `cd web && npm run dev`
3. Create a simulation with the `simple_town` scenario
4. Advance through phases and observe:
   - Events tab populates with LLM-generated events
   - Actions tab shows resolutions with outcomes
   - Actors tab displays updated traits/skills
   - Logs tab shows detailed phase execution notes

## Future Enhancements

- [ ] Real-time WebSocket updates for live simulation viewing
- [ ] Timeline visualization for event/action sequences
- [ ] Actor relationship graph
- [ ] Event/action filtering and search
- [ ] Detailed analytics dashboard with charts
- [ ] Scenario comparison tools
- [ ] Export simulation state as narrative text
