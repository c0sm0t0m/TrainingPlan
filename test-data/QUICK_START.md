# Quick Reference: Test Data Usage

## 📁 Files in this folder

1. **`ai-training-plan-config.json`** - The test data configuration
2. **`auto-fill-training-plan.js`** - Browser console script for UI auto-fill
3. **`test_ai_plan_config.py`** - Python helper for API testing
4. **`README.md`** - Detailed documentation

## 🚀 Quick Start

### For UI Testing (Frontend)

1. Start the app:
   ```bash
   ./start-all.sh
   ```

2. Open browser: http://localhost:5173/ai-training-plan

3. Open DevTools console (F12)

4. Copy and paste the entire contents of `auto-fill-training-plan.js`

5. Press Enter - the form will auto-fill!

### For API Testing (Backend)

1. Run the helper script:
   ```bash
   python3 test-data/test_ai_plan_config.py
   ```

2. Copy the generated curl command or Python code

3. Replace `YOUR_TOKEN_HERE` with actual JWT token

4. Execute the command

## 📋 Test Data Details

- **Event**: Berlin Marathon 2026 (Sep 27, 2026)
- **Goal**: Sub-3:30 marathon (3:30:00)
- **Start**: Next Monday (auto-calculated)
- **Training**: 5 days/week
- **Days**: Mon, Tue, Thu, Sat, Sun
- **Constraints**:
  - Tuesday: Track session @ 6pm
  - Thursday: Swim technique @ 8pm

## 🔧 Modifying Test Data

Edit `ai-training-plan-config.json`:

```json
{
  "eventName": "Your Event Name",
  "eventDate": "YYYY-MM-DD",
  "eventDistance": "Distance description",
  "goalTime": "HH:MM:SS",
  "startDate": "AUTO_NEXT_MONDAY",
  "trainingDaysPerWeek": 5,
  "preferredTrainingDays": ["monday", "tuesday", ...],
  "additionalNotes": "Your constraints here"
}
```

**Note**: Use `"AUTO_NEXT_MONDAY"` for startDate to always calculate next Monday.

## 💡 Tips

1. **Auto-fill not working?** Check you're on the correct page and step
2. **API test failing?** Make sure backend is running and you have valid auth token
3. **Need different event?** Just edit the JSON file
4. **Want multiple configs?** Create copies: `marathon-config.json`, `half-marathon-config.json`, etc.

## 🎯 Common Use Cases

### Testing Different Event Types

```bash
# Marathon
cp ai-training-plan-config.json marathon-config.json

# Half Marathon - Edit these fields:
# - eventDistance: "Half Marathon (21.097 km)"
# - goalTime: "1:45:00"
# - trainingDaysPerWeek: 4

# 10K
# - eventDistance: "10K"
# - goalTime: "00:45:00"
# - trainingDaysPerWeek: 4
```

### Testing Different Training Schedules

```json
// 3-day plan (weekend warrior)
"trainingDaysPerWeek": 3,
"preferredTrainingDays": ["friday", "saturday", "sunday"]

// 6-day plan (serious athlete)
"trainingDaysPerWeek": 6,
"preferredTrainingDays": ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"]
```

### Testing Various Constraints

```json
"additionalNotes": "Can only train before 7am on weekdays\nPrefer outdoor runs\nNo treadmill access"
```

## 🐛 Troubleshooting

**JavaScript auto-fill not working:**
- Make sure you're on the AI Training Plan page
- Check browser console for errors
- Try navigating to step 1 or 2 manually first

**Python script errors:**
- Ensure you're in the project root directory
- Use `python3` instead of `python`
- Check that the JSON file exists

**API returns 401:**
- You need to authenticate first
- Get a JWT token from the login endpoint
- Replace `YOUR_TOKEN_HERE` in the test commands
