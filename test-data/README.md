# Test Data

This folder contains test data for various features in the Kinesis application.

## AI Training Plan Configuration

### `ai-training-plan-config.json`

Pre-configured test data for the AI Training Plan Generator UI.

**Features:**
- **Event**: Berlin Marathon 2026 (September 27, 2026)
- **Goal Time**: 3:30:00 (sub-3:30 marathon)
- **Training Start**: Automatically set to next Monday
- **Training Days**: 5 days per week
- **Preferred Days**: Monday, Tuesday, Thursday, Saturday, Sunday
- **Constraints**:
  - Tuesdays: Running track session at 6 pm (fixed time)
  - Thursdays: 8pm swim technique session (fixed time)

### Usage

#### Option 1: Copy Configuration to Browser Console

When on the AI Training Plan Generator page (`/ai-training-plan`), open browser console and run:

```javascript
// Load test configuration
const testConfig = {
  "eventName": "Berlin Marathon 2026",
  "eventDate": "2026-09-27",
  "eventDistance": "Marathon (42.195 km)",
  "goalTime": "3:30:00",
  "trainingDaysPerWeek": 5,
  "preferredTrainingDays": ["monday", "tuesday", "thursday", "saturday", "sunday"],
  "additionalNotes": "Tuesdays: Running track session at 6 pm always\nThursdays: 8pm swim technique session."
};

// Calculate next Monday
function getNextMonday() {
  const today = new Date();
  const day = today.getDay();
  const daysUntilMonday = day === 0 ? 1 : day === 1 ? 7 : 8 - day;
  const nextMonday = new Date(today);
  nextMonday.setDate(today.getDate() + daysUntilMonday);
  return nextMonday.toISOString().split('T')[0];
}

// Fill form fields (React state setters would need to be exposed or use React DevTools)
console.log("Test Configuration:", testConfig);
console.log("Start Date (next Monday):", getNextMonday());
```

#### Option 2: Use Browser Extension (for automatic form filling)

Install a form filler extension like:
- Form Filler (Chrome/Edge)
- Autofill (Firefox)
- Formillia (Multi-browser)

Import this JSON as a profile.

#### Option 3: Modify Component for Development

During development, you can add a "Load Test Data" button to the AI Training Plan Generator component:

```typescript
const loadTestData = () => {
  setEventName("Berlin Marathon 2026");
  setEventDate("2026-09-27");
  setEventDistance("Marathon (42.195 km)");
  setGoalTime("3:30:00");
  setTrainingDaysPerWeek(5);
  setPreferredDays(["monday", "tuesday", "thursday", "saturday", "sunday"]);
  setAdditionalNotes("Tuesdays: Running track session at 6 pm always\nThursdays: 8pm swim technique session.");
};
```

## Future Test Data

More test data files can be added here:
- Sample events
- Sample workouts
- Sample activities
- Mock Garmin API responses
- Training plan templates
- Zone configurations
