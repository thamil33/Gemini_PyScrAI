# Integration Testing Checklist

## Pre-Test Setup

### Backend Configuration
- [ ] OpenRouter API key configured in `config/settings.toml`
- [ ] LLM provider set to "openrouter" in settings
- [ ] Default model configured (e.g., "anthropic/claude-3.5-sonnet")
- [ ] Memory backend storage path accessible

### Start Services
```bash
# Terminal 1: Start API Server
python run_api.py

# Terminal 2: Start Frontend Dev Server
cd web
npm run dev
```

- [ ] API server running on http://localhost:8000
- [ ] Frontend dev server running on http://localhost:5173
- [ ] No startup errors in either terminal

## Basic Functionality Tests

### 1. Simulation Creation
- [ ] Navigate to frontend URL in browser
- [ ] Fill out "Create Simulation" form:
  - Name: "Integration Test"
  - Scenario: "simple_town"
- [ ] Click "Create" button
- [ ] Simulation appears in "Simulations" list
- [ ] Simulation is automatically selected (becomes activeSimulation)
- [ ] Dashboard appears below control panel

### 2. Dashboard Overview Tab
- [ ] Overview tab is active by default
- [ ] **Current Phase** metric card shows:
  - Phase name (should be "INITIALIZE" initially)
  - Cycle number (should be 0)
- [ ] **Active Actors** metric card shows:
  - Count > 0 (simple_town seeds actors)
- [ ] **Pending Events** metric card shows:
  - Count (may be 0 initially)
- [ ] **Pending Actions** metric card shows:
  - Count (may be 0 initially)
- [ ] **Simulation Details** section shows:
  - Name: "Integration Test"
  - Scenario: "simple_town"
  - Status: "running" (green badge)
  - Created and Last Updated timestamps
- [ ] **Phase History** section shows phases executed (initially empty)
- [ ] **Recent Activity** section shows latest phase logs (initially empty or initialize log)

### 3. Phase Progression
- [ ] Click "Advance Phase" button in Control Panel
- [ ] Wait for phase to complete (spinner should show briefly)
- [ ] **Current Phase** metric updates to next phase
- [ ] Cycle number increments appropriately
- [ ] Phase History updates with new phase entry

## Event Generation Testing

### 4. First Event Generation Cycle
- [ ] Advance simulation to **EVENT_GENERATION** phase
- [ ] Switch to **Events** tab in dashboard
- [ ] Verify events appear (LLM should generate scenario seed events)
- [ ] Check each event card displays:
  - **Event Title/Description** (LLM-generated text)
  - **Event Type** with correct color:
    - Social = blue background
    - Environmental = green background
    - Economic = yellow background
    - Political = purple background
  - **Status Badge** (probably "pending" or "confirmed")
  - **Timestamp** (when event was created)
  - **Affected Actors** (should show actor names if any)
  - **Location** (if event has location)
  
### 5. Subsequent Event Generation Cycles
- [ ] Advance through full cycle (all phases to next EVENT_GENERATION)
- [ ] Verify **new emergent events** appear
- [ ] Events should be contextually relevant to simulation state
- [ ] Event descriptions should be coherent narratives

## Action Resolution Testing

### 6. Action Creation (Manual)
- [ ] In Control Panel, find "Action Composer"
- [ ] Select an actor from dropdown
- [ ] Enter action description (e.g., "Teach farming to children")
- [ ] Click "Submit Action"
- [ ] Action appears in **Actions** tab

### 7. Action Resolution Cycle
- [ ] Advance simulation to **ACTION_RESOLUTION** phase
- [ ] Switch to **Actions** tab
- [ ] Verify action card shows:
  - **Priority Border** (left border colored by priority)
    - Urgent = red, High = orange, Normal = blue, Low = gray
  - **Action Type Icon** (🚶💬🤝💰👥⚔️🔬📋)
  - **Actor Name** (who's performing the action)
  - **Action Description**
  - **Status Badge** updates to "completed" or "failed"
  
### 8. Action Outcome Display
- [ ] After resolution, action card shows **Outcome** section
- [ ] Outcome text is LLM-generated (describes what happened)
- [ ] Outcome indicates success/failure
- [ ] If action generated consequence events, they appear in Events tab

## World Update Testing

### 9. Actor Attribute Updates
- [ ] Advance simulation through **WORLD_UPDATE** phase
- [ ] Switch to **Actors** tab
- [ ] Select an actor affected by events/actions
- [ ] Verify actor card shows:
  - **📍 Location** (may have changed from action/event)
  - **✨ Traits** (may have new values, e.g., "leadership: high")
  - **🎯 Skills** (may have added skills, e.g., "[teaching, farming]")
  - **👤 Role** (actor's role from metadata)
  
### 10. Event Effect Application
- [ ] Compare actor attributes before and after WORLD_UPDATE phase
- [ ] Verify attributes changed based on event effects
- [ ] Check that trait values are updated logically
- [ ] Check that new skills are added if event granted them

## Phase Logging Testing

### 11. Detailed Phase Logs
- [ ] Switch to **Logs** tab
- [ ] Click to expand phase log viewer
- [ ] Verify log entries display:
  - **Phase Icon** (🚀⚡📥⚙️🌍📸)
  - **Phase Name** (e.g., "EVENT GENERATION")
  - **Border Color** (purple for event gen, orange for action res, etc.)
  - **Entry Number** (#1, #2, etc.)
  - **Timestamp**
  
### 12. Phase Notes Content
- [ ] Verify each phase log entry shows **Notes**:
  - INITIALIZE: "Simulation initialized", "Scenario 'simple_town' seeded"
  - EVENT_GENERATION: "Generated X events via LLM"
  - ACTION_COLLECTION: "Collected Y pending actions"
  - ACTION_RESOLUTION: "Resolved Z actions", "Applied effects to N actors"
  - WORLD_UPDATE: "Applied event effects to M actors"
  - SNAPSHOT: "Snapshot created for cycle X"

## Multi-Cycle Testing

### 13. Full Simulation Cycle
- [ ] Run simulation through 3-5 complete cycles
- [ ] Verify each cycle:
  - Generates new events (emergent, not just seeds)
  - Resolves actions with diverse outcomes
  - Updates actor attributes progressively
  - Logs all phases correctly
- [ ] Check that simulation **state evolves** over cycles:
  - Actors gain new traits/skills
  - Actors move to different locations
  - Events become more complex/interrelated
  - Actions reference previous events

### 14. Dashboard Data Consistency
- [ ] After multiple cycles, verify all tabs show consistent data:
  - Events tab count matches Overview metric
  - Actions tab count matches Overview metric
  - Actors tab count matches Overview metric
  - Phase log entries match phase history count

## UI/UX Testing

### 15. Tab Navigation
- [ ] Click through all 5 tabs (Overview, Events, Actions, Actors, Logs)
- [ ] Each tab loads instantly with no errors
- [ ] Tab count badges update correctly
- [ ] Active tab styling is clear (blue underline, blue text)

### 16. Responsive Design
- [ ] Resize browser window to mobile width (< 768px)
  - [ ] Metric cards stack vertically (1 column)
  - [ ] Tabs scroll horizontally if needed
  - [ ] All content remains readable
- [ ] Resize to tablet width (768px - 1024px)
  - [ ] Metric cards display in 2 columns
  - [ ] Content uses available space efficiently
- [ ] Resize to desktop width (> 1024px)
  - [ ] Metric cards display in 4 columns
  - [ ] Multi-column layouts activate

### 17. Dark Mode
- [ ] Toggle dark mode (if your DashboardLayout has toggle)
- [ ] Verify all components adapt:
  - [ ] Backgrounds change (white → gray-800, gray-50 → gray-900)
  - [ ] Text colors invert (gray-900 → white, gray-600 → gray-400)
  - [ ] Borders adjust (gray-200 → gray-700)
  - [ ] Badges use dark variants (blue-100 → blue-900/20)
- [ ] All text remains legible in dark mode

### 18. Empty States
- [ ] Create a new simulation (fresh state)
- [ ] Check empty states display correctly:
  - [ ] Events tab: "No events available yet"
  - [ ] Actions tab: "No actions available yet"
  - [ ] Logs tab: "No phase logs available yet"

## Performance Testing

### 19. Large Data Sets
- [ ] Run simulation for 10+ cycles to accumulate data
- [ ] Verify UI remains responsive:
  - [ ] Tab switching is still instant
  - [ ] Event/action cards render quickly
  - [ ] Scrolling is smooth
  - [ ] No browser console errors

### 20. Polling/Updates
- [ ] Keep frontend open while advancing phases
- [ ] Verify dashboard updates automatically (polling should refresh)
- [ ] Changes appear within polling interval (default: 2 seconds)
- [ ] No duplicate data or flickering

## Error Handling Testing

### 21. Backend Disconnection
- [ ] Stop API server (Ctrl+C in terminal)
- [ ] Advance phase in UI
- [ ] Verify error message appears (red banner at top)
- [ ] Error message is clear (e.g., "Failed to fetch simulation")
- [ ] Can dismiss error with X button

### 22. LLM Failures
- [ ] Temporarily break LLM config (invalid API key)
- [ ] Advance to EVENT_GENERATION phase
- [ ] Check backend logs for LLM error
- [ ] Verify fallback behavior (should not crash, may generate empty events)
- [ ] Phase log should note error or fallback

## Integration Verification

### 23. End-to-End Flow
Complete this full workflow without errors:

1. [ ] Create simulation "E2E Test" with simple_town scenario
2. [ ] Verify Overview shows seeded actors
3. [ ] Advance to EVENT_GENERATION → check Events tab for generated events
4. [ ] Manually add action via Action Composer
5. [ ] Advance to ACTION_RESOLUTION → check Actions tab for outcome
6. [ ] Check Actors tab for updated traits/skills
7. [ ] Advance to WORLD_UPDATE → verify event effects applied
8. [ ] Check Logs tab for complete phase history
9. [ ] Repeat cycle 2 more times
10. [ ] Verify simulation state is evolving logically

### 24. LLM Content Quality
Review LLM-generated content for quality:

- [ ] **Event Descriptions** are coherent narratives (not gibberish)
- [ ] **Action Outcomes** relate to action descriptions
- [ ] **Actor Trait Updates** make logical sense (e.g., teaching improves teaching skill)
- [ ] **Phase Notes** accurately summarize what happened
- [ ] **Consequence Events** are contextually relevant to actions

## Success Criteria

✅ **All tests pass** if:

1. All dashboard tabs display correct data
2. Event/action cards show proper color coding and icons
3. Actor attributes update based on LLM decisions
4. Phase logs show detailed execution notes
5. UI is responsive across all screen sizes
6. Dark mode works correctly
7. Empty states display helpful messages
8. No TypeScript/React errors in browser console
9. No unhandled exceptions in API logs
10. Simulation state evolves coherently over multiple cycles

## Common Issues & Solutions

### Issue: Events not appearing
**Solution**: Check that LLM API key is valid, verify backend logs for LLM errors, ensure EVENT_GENERATION phase completed successfully

### Issue: Actions not resolving
**Solution**: Verify actions have valid actor_id, check ACTION_RESOLUTION phase logs, ensure LLM service is responding

### Issue: Actor attributes not updating
**Solution**: Check WORLD_UPDATE and ACTION_RESOLUTION logs, verify events/actions have effects defined, ensure actor repository is saving changes

### Issue: Dashboard not updating
**Solution**: Verify polling is active (check Network tab for periodic requests), refresh page to force update, check activeSimulation is set correctly

### Issue: Colors not displaying correctly
**Solution**: Verify TailwindCSS is loaded (check for styles.css in Network tab), check for CSS conflicts, try hard refresh (Ctrl+Shift+R)

---

**Testing Complete**: When all checkboxes are marked ✅, the UI integration is fully functional!
