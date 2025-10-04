# 🚀 Quick Start: Testing the Consolidated Dashboard

## Prerequisites

- Backend API running (`python run_api.py`)
- Frontend dev server running (`cd web && npm run dev`)
- OpenRouter API key configured in `config/settings.toml`

## 30-Second Walkthrough

### 1. Create Simulation (10 seconds)
```
http://localhost:5173 → Fill form:
- Name: "Quick Test"
- Scenario: "simple_town"
→ Click "Create"
```

### 2. Explore Dashboard (10 seconds)
```
✅ Control bar at top shows:
   - Simulation name "Quick Test"
   - Current phase: INITIALIZE
   - Metrics: Actors, Events, Actions
   - Start button

✅ Workspace mode shows (default view):
   - Left: Event & Action mediation panels
   - Right: Action composer + Actors
   - Bottom: Phase logs
```

### 3. Run Simulation (10 seconds)
```
1. Click "▶️ Start" in control bar
2. Click "⏭️ Advance" to EVENT_GENERATION
3. See LLM events appear in mediation panel
4. Click "⏭️ Advance" through phases
5. Watch action outcomes populate
```

## 3-Minute Full Test

### Minute 1: View Modes
```
🎛️ Workspace Mode:
- Event mediation panel with color coding
- Action queue with priority borders
- Compact action composer in sidebar
- Actors quick view with traits/skills

🗺️ Map Mode:
- Placeholder with planned features
- "Coming Soon" message

📊 Data Mode:
- 5 tabs: Overview, Events, Actions, Actors, Logs
- Full data tables with all metadata
```

### Minute 2: Mediation Workflow
```
1. Advance to EVENT_GENERATION
   ✅ Events appear in "🔍 Event Review & Mediation"
   ✅ Color-coded by type (blue, green, yellow, purple, gray)
   ✅ Status badges visible

2. Inject Action:
   ✅ Click actor button in composer
   ✅ Enter intent: "Organize community meeting"
   ✅ Submit → appears in "⚙️ Action Queue & Resolution"

3. Advance to ACTION_RESOLUTION
   ✅ Action outcome appears with LLM description
   ✅ Actor attributes update (check Actors panel)
```

### Minute 3: Analytics & Logs
```
1. Click "📊 Data" view mode
   ✅ Overview tab shows simulation details
   ✅ Events tab lists all events with metadata
   ✅ Actions tab shows action history
   ✅ Logs tab displays phase execution notes

2. Back to workspace
   ✅ Click "🎛️ Workspace"
   ✅ Expand phase logs at bottom
   ✅ See detailed execution notes
```

## Key Features to Verify

### ✅ Consolidated Interface
- [ ] Single dashboard when simulation active
- [ ] No redundant panels or duplicate info
- [ ] All controls accessible without scrolling (desktop)

### ✅ Researcher Mediation
- [ ] Event review panel prominent and clear
- [ ] Action outcomes visible after resolution
- [ ] Actor attribute changes reflected immediately
- [ ] Phase logs show LLM operation details

### ✅ View Mode Switching
- [ ] Workspace → Map → Data → Workspace works smoothly
- [ ] No data loss when switching modes
- [ ] Active mode highlighted in control bar

### ✅ Responsive Design
- [ ] Desktop (>1024px): 3-column workspace layout
- [ ] Tablet (768-1024px): 2-column responsive grid
- [ ] Mobile (<768px): Single column stacked panels

### ✅ Dark Mode
- [ ] All components visible in dark mode
- [ ] Text legible on all backgrounds
- [ ] Borders/shadows consistent

## Common Issues & Solutions

### Issue: "No events appearing in mediation panel"
**Solution**: 
- Ensure you've advanced to EVENT_GENERATION phase
- Check LLM API key is configured
- Verify backend logs for LLM errors

### Issue: "Action composer not showing actors"
**Solution**:
- Actors appear after simulation starts (INITIALIZE phase completes)
- Check that scenario seeded actors (simple_town should have 3-5)

### Issue: "Dashboard not updating after phase advance"
**Solution**:
- Wait 2 seconds for polling to refresh
- Check browser console for API errors
- Manually refresh page to force update

### Issue: "View modes not switching"
**Solution**:
- Ensure simulation is active (not just selected)
- Check that activeSimulation is set in store
- Try hard refresh (Ctrl+Shift+R)

## Screenshot Verification Checklist

When taking screenshots for documentation:

### Workspace Mode
- [ ] Full control bar visible at top
- [ ] Event mediation panel with colored events
- [ ] Action queue panel with priority borders
- [ ] Action composer in right sidebar
- [ ] Actors quick view below composer
- [ ] Phase logs at bottom (can be collapsed)

### Map Mode
- [ ] Placeholder message centered
- [ ] List of planned features visible
- [ ] Simulation name shown

### Data Mode
- [ ] 5 tabs visible in tab bar
- [ ] Tab counts (badges) showing
- [ ] Content area showing selected tab data

## Performance Targets

- [ ] Page load < 2 seconds
- [ ] View mode switch < 200ms
- [ ] Phase advance request < 1 second (LLM dependent)
- [ ] Polling update < 100ms processing
- [ ] Smooth scrolling on all panels

## Test Data Expectations

After 3 full cycles (INITIALIZE → EVENT_GENERATION → ACTION_COLLECTION → ACTION_RESOLUTION → WORLD_UPDATE → SNAPSHOT × 3):

**Events**:
- ~5-10 LLM-generated events
- Mix of social, environmental, economic types
- Some confirmed, some resolved

**Actions**:
- 1-2 manually injected (from testing)
- Some completed with outcomes
- Outcomes should be coherent narratives

**Actors**:
- 3-5 actors from simple_town scenario
- Traits: should have key-value pairs (e.g., "leadership: high")
- Skills: should have arrays (e.g., ["teaching", "mentoring"])
- Locations: may have changed from actions/events

**Logs**:
- ~18 phase log entries (6 phases × 3 cycles)
- Each with phase-specific icon and color
- Notes include "Generated X events via LLM", "Resolved Y actions", etc.

## Success Criteria

✅ **Interface is ready** if:

1. You can create simulation and see consolidated dashboard
2. View modes switch smoothly without errors
3. Events appear in mediation panel with proper styling
4. Actions can be injected and outcomes displayed
5. Actors show updated traits/skills after world update
6. Phase logs show detailed execution notes
7. Responsive design works on mobile/tablet/desktop
8. Dark mode supported throughout
9. No TypeScript errors in browser console
10. No unhandled exceptions in API logs

## Next Steps After Verification

1. **Gather Feedback**: Show to actual researchers, note pain points
2. **Event Editing**: Implement inline editing of LLM events
3. **Map Integration**: Add Leaflet.js to Map mode
4. **Real-time Updates**: Replace polling with WebSocket
5. **Export Features**: Add narrative/data export capabilities

---

**Estimated Testing Time**: 3-5 minutes for full walkthrough

**Status**: ✅ Ready for Testing - All Components Integrated
