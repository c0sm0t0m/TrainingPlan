# Breadcrumbs & Quick Actions - Visual Guide

## 🧭 Breadcrumbs Feature

### What You'll See

**Plan Detail Page**:
```
┌─────────────────────────────────────────────────┐
│ 🏠 Home > Training Plans > 5K Training Plan    │
│                                  ▲              │
│ ← Back to Plans             Clickable          │
│                                                 │
│ 5K Training Plan                           Run │
│ Beginner-friendly 5K training program          │
│ ...                                             │
└─────────────────────────────────────────────────┘
```

**Settings Page**:
```
┌─────────────────────────────────────────────────┐
│ 🏠 Home > ⚙️ Settings                          │
│                                                 │
│ Settings                                        │
│ [Training Zones] [Integrations] [Beta Features]│
│ ...                                             │
└─────────────────────────────────────────────────┘
```

### How to Enable

1. Navigate to **Settings** (⚙️ icon in top-right)
2. Click **Beta Features** tab
3. Under "High-Impact Features (P1)", find:
   - ☑️ **Breadcrumbs** toggle
4. Toggle ON
5. Visit Training Plans → Click a plan → See breadcrumbs appear!

### User Experience

- **Before**: Only "← Back to Plans" button, no context
- **After**: Full path visible, click any level to navigate up

---

## ⚡ Quick Actions FAB

### What You'll See

**Dashboard Page**:
```
┌─────────────────────────────────────────────────┐
│ Training Dashboard                              │
│                                                 │
│ [Fitness Card] [Fatigue Card] [Form Card]      │
│ [Performance Chart]                             │
│ [Sport Widgets]                                 │
│                                                 │
│                                          ╔═══╗ │
│                                          ║ ➕ ║ │ ← FAB (Click to expand)
│                                          ╚═══╝ │
└─────────────────────────────────────────────────┘
     Expanded SpeedDial:
     ┌───────────────────┐
     │ 📋 New Plan       │
     │ 📅 View Calendar  │
     │ 🏃 Log Activity   │
     └───────────────────┘
```

**Training Plans Page**:
```
┌─────────────────────────────────────────────────┐
│ Training Plans               [New Plan]         │
│                                                 │
│ [Plan Card] [Plan Card] [Plan Card]            │
│                                                 │
│                                          ╔═══╗ │
│                                          ║ ➕ ║ │ ← Single FAB
│                                          ╚═══╝ │
│                                    Create Plan  │
└─────────────────────────────────────────────────┘
```

**Plan Detail Page**:
```
┌─────────────────────────────────────────────────┐
│ 5K Training Plan                           Run  │
│                                                 │
│ Workouts (12)                [Import XML] [Add] │
│ [Workout Table]                                 │
│                                                 │
│                                          ╔═══╗ │
│                                          ║ ➕ ║ │ ← FAB (Click to expand)
│                                          ╚═══╝ │
└─────────────────────────────────────────────────┘
     Expanded SpeedDial:
     ┌───────────────────┐
     │ 🏃 Add Run        │
     │ 🚴 Add Ride       │
     │ 🏊 Add Swim       │
     └───────────────────┘
```

**Calendar Page**:
```
┌─────────────────────────────────────────────────┐
│ ◀ November 2025                           ▶     │
│                                                 │
│ Mon Tue Wed Thu Fri Sat Sun                    │
│ [Calendar Grid with Workouts]                  │
│                                                 │
│                                          ╔═══╗ │
│                                          ║ ➕ ║ │ ← FAB (Click to expand)
│                                          ╚═══╝ │
└─────────────────────────────────────────────────┘
     Expanded SpeedDial:
     ┌───────────────────┐
     │ 📋 View Plans     │
     │ 📅 Today          │
     └───────────────────┘
```

### How to Enable

1. Navigate to **Settings** → **Beta Features**
2. Under "High-Impact Features (P1)", find:
   - ☑️ **Quick Actions FAB** toggle
3. Toggle ON
4. Visit any page → See floating button in bottom-right corner!

### Context-Aware Actions

The FAB shows different actions based on where you are:

| Page           | Actions                                |
|----------------|----------------------------------------|
| Dashboard      | New Plan, View Calendar, Log Activity  |
| Training Plans | Create Plan (single button)           |
| Plan Detail    | Add Run, Add Ride, Add Swim           |
| Calendar       | View Plans, Go to Today                |
| Activities     | View Calendar                          |
| Settings       | Back to Dashboard                      |

---

## 🎨 Visual Design

### Breadcrumbs
- **Separator**: `>` with NavigateNext icon
- **Colors**: 
  - Active links: Inherit color (theme-aware)
  - Current page: `text.primary` with bold weight (600)
- **Icons**: Small icons (fontSize="small") for visual context
- **Hover**: Underline on clickable items

### Quick Actions FAB
- **Size**: Standard Material-UI FAB (56px)
- **Position**: Fixed bottom-right
  - Desktop: 24px from edges
  - Mobile: 16px from edges
- **Color**: `primary` (blue)
- **Icon**: 
  - Single action: Action-specific icon (➕, 🏠)
  - Multiple actions: SpeedDialIcon (➕ → ✕)
- **Animation**: Smooth expand/collapse
- **z-index**: 1000 (above content, below modals)

---

## 📱 Mobile Experience

### Breadcrumbs on Mobile
```
Small Screen (<600px):
┌──────────────────────────┐
│ 🏠 Home >                │
│ Training Plans >          │
│ 5K Training Plan         │ ← May wrap to new lines
│                          │
│ ← Back to Plans          │
└──────────────────────────┘
```

### FAB on Mobile
- Positioned 16px from bottom-right
- Touch-friendly size (48px min)
- SpeedDial opens upward (above FAB)
- Tooltips shown on long-press

---

## 🌙 Dark Mode

Both features fully support dark mode:

### Breadcrumbs
- Links: Inherit theme color (white in dark mode)
- Current page: `text.primary` (white/off-white)
- Separator: Theme-aware grey

### Quick Actions FAB
- Primary color adjusts to dark theme
- SpeedDial backdrop: Semi-transparent black
- Action icons: White on dark background
- Tooltips: Dark background with white text

---

## 🧪 Testing Your Implementation

### Quick Test (2 minutes)

1. **Enable Features**:
   ```
   Settings → Beta Features → Enable both:
   - ☑️ Breadcrumbs
   - ☑️ Quick Actions FAB
   ```

2. **Test Breadcrumbs**:
   - Visit Training Plans
   - Click any plan
   - See: `Home > Training Plans > [Plan Name]`
   - Click "Training Plans" → Should go back

3. **Test FAB**:
   - Visit Dashboard
   - See FAB in bottom-right
   - Click to expand → See 3 actions
   - Click "New Plan" → Should navigate to /plans

4. **Test Dark Mode**:
   - Toggle dark mode (sun/moon icon)
   - Breadcrumbs remain readable
   - FAB contrast maintained

### URL Override Test

Test without changing settings:
```
http://localhost:5173/?newBreadcrumbs=true&newQuickActions=true
```

---

## 🎯 Success Metrics

Track these after deployment:

**Breadcrumbs**:
- Click-through rate on breadcrumb links
- Reduction in "back button" usage
- User survey: "I always know where I am" (1-5 scale)

**Quick Actions FAB**:
- FAB usage rate vs traditional navigation
- Time to complete common tasks (create plan, add workout)
- User survey: "FAB makes the app faster" (1-5 scale)

**Combined Impact**:
- Overall reduction in navigation clicks
- Decreased user confusion/support requests
- Increased feature discovery

---

## 🐛 Troubleshooting

### Breadcrumbs Not Showing
- ✅ Check feature flag is enabled (Settings → Beta Features)
- ✅ Refresh page after enabling
- ✅ Only shows on PlanDetail and Settings pages (by design)

### FAB Not Showing
- ✅ Check feature flag is enabled
- ✅ Not visible on login/register pages (by design)
- ✅ Check browser console for errors

### FAB Overlapping Content
- FAB positioned with fixed positioning and z-index: 1000
- Ensure page content has padding-bottom to avoid overlap
- On mobile, may need to scroll to see bottom content

### Dark Mode Issues
- Breadcrumbs/FAB should automatically adapt
- If not, check theme is properly applied in App.tsx
- Clear browser cache and refresh

---

**Happy Testing! 🚀**

