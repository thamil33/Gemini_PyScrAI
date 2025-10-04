# ScrAI Visual Reference Guide

Quick reference for understanding the color coding and visual indicators in the ScrAI UI.

## 🎨 Event Color Coding

| Type | Background | Text | Icon | Example |
|------|-----------|------|------|---------|
| **Social** | `bg-blue-100` | `text-blue-900` | 🔵 | Village meeting, social gathering |
| **Environmental** | `bg-green-100` | `text-green-900` | 🟢 | Weather change, natural disaster |
| **Economic** | `bg-yellow-100` | `text-yellow-900` | 🟡 | Market fluctuation, trade event |
| **Political** | `bg-purple-100` | `text-purple-900` | 🟣 | Election, policy change |
| **System** | `bg-gray-100` | `text-gray-900` | ⚫ | Simulation meta-events |

## 📊 Event Status Badges

| Status | Badge Color | Icon | Meaning |
|--------|------------|------|---------|
| **Pending** | `bg-yellow-100 text-yellow-800` | 🟡 | Event awaiting processing |
| **Confirmed** | `bg-blue-100 text-blue-800` | 🔵 | Event validated and active |
| **Resolved** | `bg-green-100 text-green-800` | 🟢 | Event completed |
| **Cancelled** | `bg-red-100 text-red-800` | 🔴 | Event invalidated |

## ⚡ Action Priority Borders

| Priority | Left Border | Color Code | Use Case |
|----------|------------|------------|----------|
| **Urgent** | 4px `border-red-300` | 🔴 | Critical actions requiring immediate attention |
| **High** | 4px `border-orange-300` | 🟠 | Important actions |
| **Normal** | 4px `border-blue-300` | 🔵 | Standard priority actions |
| **Low** | 4px `border-gray-300` | ⚫ | Background tasks |

## 🎯 Action Type Icons

| Type | Icon | Description |
|------|------|-------------|
| **Movement** | 🚶 | Actor changes location |
| **Communication** | 💬 | Dialogue, messages, speeches |
| **Interaction** | 🤝 | Social interactions, meetings |
| **Economic** | 💰 | Trade, transactions, economic activities |
| **Social** | 👥 | Group activities, community events |
| **Combat** | ⚔️ | Conflicts, battles |
| **Research** | 🔬 | Investigation, learning |
| **Custom** | 📋 | User-defined actions |

## 📝 Action Status Badges

| Status | Badge Color | Meaning |
|--------|------------|---------|
| **Pending** | `bg-yellow-100 text-yellow-800` | Awaiting resolution |
| **Active** | `bg-blue-100 text-blue-800` | Currently being processed |
| **Completed** | `bg-green-100 text-green-800` | Successfully resolved |
| **Failed** | `bg-red-100 text-red-800` | Resolution failed |
| **Cancelled** | `bg-gray-100 text-gray-800` | Action cancelled |

## 🔄 Phase Indicators

| Phase | Icon | Border Color | Description |
|-------|------|-------------|-------------|
| **Initialize** | 🚀 | `border-gray-500` | Scenario seeding, setup |
| **Event Generation** | ⚡ | `border-purple-500` | LLM generates new events |
| **Action Collection** | 📥 | `border-blue-500` | Gather pending actions |
| **Action Resolution** | ⚙️ | `border-orange-500` | LLM resolves actions |
| **World Update** | 🌍 | `border-green-500` | Apply event effects |
| **Snapshot** | 📸 | `border-cyan-500` | Record state |

## 👤 Actor Attribute Icons

| Attribute | Icon | Display Format | Example |
|-----------|------|---------------|---------|
| **Location** | 📍 | `📍 {location_name}` | 📍 Town Hall |
| **Traits** | ✨ | `✨ {key}: {value}` | ✨ leadership: high |
| **Skills** | 🎯 | `🎯 [{skill1}, {skill2}]` | 🎯 [teaching, mentoring] |
| **Role** | 👤 | `👤 {role}` | 👤 teacher |

## 📈 Simulation Status

| Status | Badge Color | Icon | Meaning |
|--------|------------|------|---------|
| **Running** | `bg-green-100 text-green-800` | 🟢 | Simulation actively progressing |
| **Paused** | `bg-yellow-100 text-yellow-800` | 🟡 | Simulation paused |
| **Completed** | `bg-blue-100 text-blue-800` | 🔵 | Simulation finished |
| **Error** | `bg-red-100 text-red-800` | 🔴 | Simulation error state |

## 🎨 Dashboard Metric Cards

| Metric | Gradient | Border | Icon/Label |
|--------|----------|--------|------------|
| **Current Phase** | `from-blue-50 to-blue-100` | `border-blue-200` | Phase name + cycle number |
| **Active Actors** | `from-green-50 to-green-100` | `border-green-200` | Actor count |
| **Pending Events** | `from-purple-50 to-purple-100` | `border-purple-200` | Event count |
| **Pending Actions** | `from-orange-50 to-orange-100` | `border-orange-200` | Action count |

## 🌗 Dark Mode Equivalents

All components support dark mode with these conversions:

| Light Mode | Dark Mode |
|------------|-----------|
| `bg-white` | `bg-gray-800` |
| `bg-gray-50` | `bg-gray-900` |
| `bg-gray-100` | `bg-gray-700` |
| `text-gray-900` | `text-white` |
| `text-gray-600` | `text-gray-400` |
| `border-gray-200` | `border-gray-700` |

Color badges automatically adjust:
- Light: `bg-blue-100 text-blue-800`
- Dark: `dark:bg-blue-900/20 dark:text-blue-400`

## 📐 Component Dimensions

| Component | Width | Height | Scroll |
|-----------|-------|--------|--------|
| **Dashboard Tabs** | Full width | Auto | Horizontal scroll on mobile |
| **Metric Cards** | 1/4 grid | Auto | No scroll |
| **Event Cards** | Full width | Auto | Vertical scroll container |
| **Action Cards** | Full width | Auto | Vertical scroll container |
| **Actor Cards** | Full width | Auto | Vertical scroll container |
| **Phase Log Entries** | Full width | Auto | `max-h-96` scroll |

## 🎯 Interactive States

### Hover States
```css
hover:bg-gray-50 dark:hover:bg-gray-700/50  /* Cards */
hover:bg-blue-600 dark:hover:bg-blue-700    /* Buttons */
```

### Active Tab
```css
text-blue-600 dark:text-blue-400
border-b-2 border-blue-600 dark:border-blue-400
bg-blue-50 dark:bg-blue-900/20
```

### Inactive Tab
```css
text-gray-600 dark:text-gray-400
hover:text-gray-900 dark:hover:text-gray-200
hover:bg-gray-50 dark:hover:bg-gray-700/50
```

### Expandable Sections
- **Collapsed**: Chevron pointing right, "Click to expand" text
- **Expanded**: Chevron pointing down (rotated 90deg), content visible

## 🔤 Typography Scale

| Element | Class | Size | Weight |
|---------|-------|------|--------|
| **Page Title** | `text-2xl` | 1.5rem | `font-bold` |
| **Section Heading** | `text-lg` | 1.125rem | `font-semibold` |
| **Card Title** | `text-base` | 1rem | `font-medium` |
| **Body Text** | `text-sm` | 0.875rem | `font-normal` |
| **Metadata** | `text-xs` | 0.75rem | `font-normal` |

## 📱 Responsive Breakpoints

| Breakpoint | Width | Layout |
|------------|-------|--------|
| **Mobile** | < 768px | Single column, stacked cards |
| **Tablet** | 768px - 1024px | 2-column grid |
| **Desktop** | > 1024px | Multi-column with sidebar |

Grid classes:
```css
grid-cols-1 md:grid-cols-2 lg:grid-cols-4  /* Metric cards */
grid-cols-1 lg:grid-cols-2                  /* Main layout */
```

## 🎨 Quick Reference Card

**Most Common Patterns:**

1. **Card Container**: `bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700`

2. **Card Header**: `px-6 py-4 border-b border-gray-200 dark:border-gray-700`

3. **Card Content**: `p-6 space-y-4`

4. **Badge**: `px-2 py-1 text-xs rounded-full bg-{color}-100 dark:bg-{color}-900/20 text-{color}-800 dark:text-{color}-400`

5. **Button Primary**: `px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700`

6. **Button Secondary**: `px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300`

---

**Pro Tip**: Use browser DevTools to inspect any component and see the exact Tailwind classes applied!
