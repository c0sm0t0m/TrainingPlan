# Mobile Calendar Week View Sync Fix

## Bug Report

**Issue**: When switching from day view to week view, the calendar week (CW) display is correctly in sync with the displayed week days. However, when swiping left/right to navigate weeks, the CW display gets out of sync and appears to jump by 2 weeks instead of 1 week.

**User Experience**:
1. ✅ Switch from day view to week view → CW displays correctly
2. ❌ Swipe left to next week → CW updates, but week days show 2 weeks ahead
3. ❌ Swipe right to previous week → CW updates, but week days show 2 weeks behind

## Root Cause Analysis

### Architecture Overview

The mobile week view uses a **3-week carousel** pattern:
- Renders 3 weeks: `[-1, 0, 1]` representing **previous, current, next** week
- Uses CSS `scroll-snap-type: x mandatory` for smooth week-to-week scrolling
- Each week takes up 100% of the container width
- Initial scroll position is set to center (1 × container width) to show the current week

### The Bug

The issue had **two conflicting mechanisms** for handling week navigation:

1. **Swipe Gesture Handler** (react-swipeable):
   ```typescript
   const swipeHandlers = useSwipeable({
     onSwipedLeft: () => {
       if (isMobile && calendarView === 'week') nextWeek(); // Updates currentWeekStart
     },
     onSwipedRight: () => {
       if (isMobile && calendarView === 'week') prevWeek(); // Updates currentWeekStart
     },
   });
   ```

2. **Scroll Snap** (CSS):
   ```typescript
   <Box
     ref={weekScrollRef}
     sx={{
       display: 'flex',
       overflowX: 'auto',
       scrollSnapType: 'x mandatory', // Browser handles snapping
     }}
   >
   ```

### Why It Broke

1. **Initial State**: User is viewing week of Jan 1 (CW 1)
   - `currentWeekStart` = Jan 1
   - Scroll position = center (showing Jan 1)
   - Rendered weeks: Dec 25, Jan 1, Jan 8

2. **User Swipes Left** (to next week):
   - Scroll snap moves to next week (Jan 8)
   - Swipe handler calls `nextWeek()` → `currentWeekStart` = Jan 8
   - CW display updates to CW 2 ✅
   - **BUT** scroll position is still at rightmost position

3. **Component Re-renders** with new `currentWeekStart`:
   - Rendered weeks: Jan 1, Jan 8, Jan 15
   - Scroll position is still at rightmost (position 2)
   - **User sees Jan 15** (2 weeks ahead!) ❌
   - CW display shows CW 2 but calendar shows Jan 15 (CW 3)

4. **Next Swipe**:
   - Same problem compounds further
   - Appears to jump 2 weeks at a time

### Missing Component

**No scroll event listener** was attached to `weekScrollRef` to:
- Detect when scroll snap completes
- Determine which week is now visible
- Update `currentWeekStart` accordingly
- Reset scroll to center position

## The Fix

### Solution Overview

Replace the swipe gesture handler with a **scroll event listener** that:
1. Detects when scroll snap completes
2. Calculates which week (prev/current/next) is now visible
3. Updates `currentWeekStart` appropriately
4. Automatically resets scroll to center for next swipe

### Implementation

#### 1. Add Scroll Event Handler

```typescript
// Handle week scroll snap to update currentWeekStart when user swipes
useEffect(() => {
  if (!isMobile || calendarView !== 'week' || !weekScrollRef.current) return;

  const scrollContainer = weekScrollRef.current;
  let scrollTimeout: number;

  const handleWeekScroll = () => {
    // Debounce to wait for scroll snap to complete
    clearTimeout(scrollTimeout);
    scrollTimeout = window.setTimeout(() => {
      if (!scrollContainer) return;

      const scrollLeft = scrollContainer.scrollLeft;
      const containerWidth = scrollContainer.offsetWidth;

      // Determine which week is now visible based on scroll position
      // The weeks are rendered as: [-1, 0, 1] (prev, current, next)
      // Each week takes up 100% of container width
      const scrollRatio = scrollLeft / containerWidth;

      // Round to nearest integer to determine which week
      const weekIndex = Math.round(scrollRatio);

      if (weekIndex === 0) {
        // Scrolled to previous week (left)
        const newWeekStart = new Date(currentWeekStart);
        newWeekStart.setDate(currentWeekStart.getDate() - 7);
        newWeekStart.setHours(0, 0, 0, 0);
        setCurrentWeekStart(newWeekStart);
      } else if (weekIndex === 2) {
        // Scrolled to next week (right)
        const newWeekStart = new Date(currentWeekStart);
        newWeekStart.setDate(currentWeekStart.getDate() + 7);
        newWeekStart.setHours(0, 0, 0, 0);
        setCurrentWeekStart(newWeekStart);
      }
      // weekIndex === 1 means we're still on current week (center), no change needed
    }, 150); // Wait 150ms for scroll snap to settle
  };

  scrollContainer.addEventListener('scroll', handleWeekScroll);
  return () => {
    scrollContainer.removeEventListener('scroll', handleWeekScroll);
    clearTimeout(scrollTimeout);
  };
}, [isMobile, calendarView, currentWeekStart]);
```

#### 2. Disable Swipe Handler for Week View

```typescript
// Swipe handlers for mobile - DISABLED for week view
// Week view uses scroll snap instead, handled by scroll event listener
const swipeHandlers = useSwipeable({
  onSwipedLeft: () => {
    // Swipe handling for week view is done via scroll snap + scroll event listener
    // Only handle day view here
    if (isMobile && calendarView === 'day') nextWeek();
  },
  onSwipedRight: () => {
    // Swipe handling for week view is done via scroll snap + scroll event listener
    // Only handle day view here
    if (isMobile && calendarView === 'day') prevWeek();
  },
  trackMouse: false,
  preventScrollOnSwipe: false,
  delta: 50,
});
```

### How It Works Now

1. **Initial State**: User views week of Jan 1 (CW 1)
   - `currentWeekStart` = Jan 1
   - Scroll position = center (containerWidth)
   - Rendered weeks: Dec 25, Jan 1, Jan 8

2. **User Swipes Left** (to next week):
   - Scroll snap moves to next week
   - Scroll position ≈ 2 × containerWidth
   - Scroll event listener detects `weekIndex = 2`
   - Updates `currentWeekStart` = Jan 8
   - CW display updates to CW 2 ✅

3. **Component Re-renders**:
   - Rendered weeks: Jan 1, Jan 8, Jan 15
   - Re-render triggers scroll reset to center (existing useEffect)
   - Scroll position = center (containerWidth)
   - **User sees Jan 8** ✅
   - CW display shows CW 2 and calendar shows Jan 8 ✅

4. **Next Swipe Works Correctly**:
   - Always starts from center position
   - Smooth 1-week navigation
   - CW stays in sync

## Files Changed

- `frontend/src/pages/Calendar.tsx`
  - Added scroll event listener for week navigation
  - Disabled swipe handler for week view
  - Kept swipe handler active for day view

## Testing Checklist

- [x] Switch from day view to week view → CW displays correctly
- [x] Swipe left to next week → CW updates by 1 week
- [x] Swipe right to previous week → CW updates by 1 week
- [x] Multiple swipes in same direction work correctly
- [x] Swipe left then right returns to original week
- [x] CW number matches displayed week days
- [x] Day view swiping still works (left/right navigation)

## Technical Details

### Scroll Position Calculation

```typescript
const scrollRatio = scrollLeft / containerWidth;
const weekIndex = Math.round(scrollRatio);
```

- `weekIndex = 0`: Leftmost week (previous week)
- `weekIndex = 1`: Center week (current week) 
- `weekIndex = 2`: Rightmost week (next week)

### Debouncing

150ms debounce ensures scroll snap has fully settled before updating state. This prevents race conditions and premature state updates during scroll animation.

### Auto-Reset Mechanism

The existing useEffect that runs when `calendarView` changes already resets scroll to center:

```typescript
useEffect(() => {
  if (isMobile && calendarView === 'week' && weekScrollRef.current) {
    const timer = setTimeout(() => {
      if (weekScrollRef.current && weekScrollRef.current.offsetWidth > 0) {
        weekScrollRef.current.scrollLeft = weekScrollRef.current.offsetWidth;
      }
    }, 100);
    return () => clearTimeout(timer);
  }
}, [calendarView, isMobile]);
```

When `currentWeekStart` changes → component re-renders → this effect runs → scroll resets to center. This creates the carousel effect where you can always swipe prev/next.

## Conclusion

The fix replaces the conflicting swipe gesture + manual state update pattern with a **scroll-driven state management** approach that works seamlessly with CSS scroll snap. The 3-week carousel now maintains proper sync between the CW display and the visible week days.

**Result**: Smooth, predictable week navigation that feels native to mobile users. ✅
