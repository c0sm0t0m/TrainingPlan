# Test Data - Complete Summary

## 📦 What's Included

This folder contains everything you need to quickly test the AI Training Plan Generator feature with pre-configured data.

### Files Created

1. **`ai-training-plan-config.json`** (13 lines)
   - JSON configuration file
   - Can be edited manually or via the HTML editor
   - Used by Python script for API testing

2. **`auto-fill-training-plan.js`** (181 lines)
   - Browser console script
   - Automatically fills the UI form with test data
   - Handles Material-UI component interactions

3. **`test_ai_plan_config.py`** (143 lines)
   - Python helper script
   - Loads config and generates test commands
   - Provides curl and Python code examples
   - Analyzes training period

4. **`test-data-editor.html`** (332 lines)
   - Standalone HTML editor
   - Visual interface for editing test data
   - Can be opened directly in any browser
   - No server required

5. **`README.md`** (156 lines)
   - Comprehensive documentation
   - Usage instructions for all tools
   - Examples and best practices

6. **`QUICK_START.md`** (173 lines)
   - Quick reference guide
   - Common use cases
   - Troubleshooting tips

## 🎯 Test Configuration Details

**Default Test Data:**
```
Event:       Berlin Marathon 2026
Date:        September 27, 2026
Distance:    Marathon (42.195 km)
Goal:        3:30:00 (sub-3:30 finish)
Start:       Next Monday (auto-calculated)
Training:    5 days per week
Days:        Monday, Tuesday, Thursday, Saturday, Sunday
Constraints: 
  • Tuesday: Running track session at 6pm (fixed)
  • Thursday: Swim technique session at 8pm (fixed)
```

## 🚀 Quick Usage

### Option 1: Visual Editor (Easiest)
```bash
# Open the HTML file in your browser
open test-data/test-data-editor.html
```
- Edit fields visually
- See live preview of training period
- Copy JSON to clipboard
- No command line needed!

### Option 2: Browser Auto-Fill
```bash
# 1. Start the app
./start-all.sh

# 2. Open browser to http://localhost:5173/ai-training-plan

# 3. Open DevTools console (F12)

# 4. Copy contents of auto-fill-training-plan.js and paste
```

### Option 3: API Testing
```bash
# Run the helper script
python3 test-data/test_ai_plan_config.py

# Copy the generated curl command
# Replace YOUR_TOKEN_HERE with real JWT
# Execute
```

### Option 4: Direct JSON Edit
```bash
# Edit the JSON file directly
code test-data/ai-training-plan-config.json

# Or use any text editor
nano test-data/ai-training-plan-config.json
```

## 💡 Common Workflows

### Testing Different Event Types

**Marathon → Half Marathon:**
```json
{
  "eventDistance": "Half Marathon (21.097 km)",
  "goalTime": "1:45:00",
  "trainingDaysPerWeek": 4
}
```

**Marathon → 10K:**
```json
{
  "eventDistance": "10K",
  "goalTime": "00:45:00",
  "trainingDaysPerWeek": 4,
  "preferredTrainingDays": ["tuesday", "thursday", "saturday", "sunday"]
}
```

### Testing Different Schedules

**Weekend Warrior (3 days):**
```json
{
  "trainingDaysPerWeek": 3,
  "preferredTrainingDays": ["friday", "saturday", "sunday"],
  "additionalNotes": "Can only train on weekends due to work schedule"
}
```

**Serious Athlete (6 days):**
```json
{
  "trainingDaysPerWeek": 6,
  "preferredTrainingDays": ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"],
  "additionalNotes": "Rest day on Friday. Focus on quality over quantity."
}
```

## 🔍 What Gets Tested

This test data exercises:

1. **Event configuration**
   - Event name, date, distance
   - Goal time setting
   - Future event date validation

2. **Training plan setup**
   - Dynamic start date calculation (next Monday)
   - Training frequency (days per week)
   - Preferred day selection

3. **Constraints handling**
   - Fixed time slots (Tuesday 6pm, Thursday 8pm)
   - Multi-line notes processing
   - Special session requirements

4. **Date calculations**
   - Next Monday algorithm
   - Training period length
   - Week counting

## 📊 Expected Results

When you use this test data, you should get:

**Training Period:**
- Start: Next Monday after today
- End: September 27, 2026
- Duration: ~36 weeks (depends on current date)

**Training Schedule:**
- 5 sessions per week
- Monday: Regular training
- Tuesday: Track session (6pm)
- Thursday: Swim technique (8pm)
- Saturday: Long run/key workout
- Sunday: Recovery or supplemental

**Warning if run on Jan 6, 2026:**
- Shows "⚠️ More than 24 weeks" because we're 36 weeks out
- For optimal testing, adjust event date to be 12-20 weeks away

## 🛠️ Customization

### Adjust Event Date for Shorter Cycle

If you want to test with a more realistic training period:

```javascript
// In test-data-editor.html or JSON file:
// Change event date to 16 weeks from next Monday
const nextMonday = getNextMonday();
const eventDate = new Date(nextMonday);
eventDate.setDate(eventDate.getDate() + (16 * 7));
```

### Add More Constraints

```json
{
  "additionalNotes": "Tuesdays: Running track session at 6 pm always\nThursdays: 8pm swim technique session.\nNo treadmill access - outdoor only\nPrefer morning runs before 7am\nCannot train on public holidays"
}
```

### Test Edge Cases

```json
// Minimal training (3 days)
{"trainingDaysPerWeek": 3, "preferredTrainingDays": ["saturday", "sunday", "wednesday"]}

// Maximum training (7 days)
{"trainingDaysPerWeek": 7, "preferredTrainingDays": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]}

// Unusual schedule (weekdays only)
{"trainingDaysPerWeek": 5, "preferredTrainingDays": ["monday", "tuesday", "wednesday", "thursday", "friday"]}
```

## 🐛 Troubleshooting

### Auto-fill script not working?
- Ensure you're on `/ai-training-plan` page
- Check you're on the correct step (step 0 or 1)
- Try reloading the page
- Check console for JavaScript errors

### Python script errors?
- Use `python3` not `python`
- Run from project root directory
- Ensure JSON file exists and is valid

### HTML editor not showing next Monday?
- Clear browser cache
- Check JavaScript console for errors
- Try a different browser (Chrome, Firefox, Safari all work)

### Generated JSON not accepted by API?
- Verify all required fields are filled
- Check date format (YYYY-MM-DD)
- Ensure at least 3 days selected
- Validate JSON syntax

## 📝 Next Steps

After using this test data:

1. **Verify AI prompt generation** - Check that prompts include your constraints
2. **Test plan import** - Upload generated plan JSON
3. **Validate calendar sync** - Ensure workouts appear on correct days
4. **Check constraints** - Verify Tuesday track and Thursday swim sessions

## 🎓 Learning Resources

- [README.md](README.md) - Detailed documentation
- [QUICK_START.md](QUICK_START.md) - Quick reference
- Open `test-data-editor.html` - Visual interface
- Run `python3 test_ai_plan_config.py` - See analysis

## 📞 Support

If you encounter issues:
1. Check the troubleshooting sections in README.md and QUICK_START.md
2. Verify you're using the latest version
3. Check that services are running (`./start-all.sh`)
4. Review browser console and backend logs

---

**Last Updated:** January 6, 2026
**Version:** 1.0.0
**Compatible with:** Kinesis v0.1.0+
