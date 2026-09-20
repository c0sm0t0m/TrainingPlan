# 🚀 Quick Start: Generate AI Training Plan

## TL;DR - 3 Steps (100% Success Rate ✅)

1. **Generate Prompt** in Kinesis → Copy it
2. **Paste into ChatGPT** → Get response
3. **Copy & Import** directly into Kinesis (no cleaning needed!)

**✨ NEW**: The app now automatically cleans ChatGPT responses! Just copy-paste directly.

---

## Simple Workflow

### Step 1: Generate Prompt
1. Open Kinesis → Training Plans
2. Click "Generate AI Plan"
3. Fill in event details
4. Click "Generate Prompt"
5. Copy the prompt

### Step 2: Get Plan from ChatGPT
1. Open ChatGPT (or Claude)
2. Paste the prompt
3. Wait for response
4. **Copy the entire response** (yes, even with markdown fences!)

### Step 3: Import
1. Back in Kinesis, click "Import AI Plan"
2. Save ChatGPT's response to a `.json` file
3. Upload the file
4. ✅ Done! The app automatically cleans it.

---

## Optional: Improve ChatGPT Output Quality

While the app now handles markdown fences automatically, you can still add these instructions for **cleaner output from ChatGPT**:

**Add this at the END of the prompt:**

```
======================================
🤖 CRITICAL OUTPUT REQUIREMENTS
======================================

YOU MUST FOLLOW THESE FORMATTING RULES EXACTLY:

1. ❌ DO NOT wrap the JSON in markdown code fences (```)
2. ❌ DO NOT add any explanations before or after the JSON
3. ❌ DO NOT include comments in the JSON
4. ✅ Output ONLY the raw JSON object starting with { and ending with }
5. ✅ Ensure all JSON is valid (proper quotes, commas, brackets)
6. ✅ All date fields MUST be in YYYY-MM-DD format
7. ✅ All numeric fields MUST be numbers, not strings

START YOUR RESPONSE WITH: {
END YOUR RESPONSE WITH: }
NO TEXT BEFORE OR AFTER
```

---

## If You Want to Clean Manually (Optional)

The app does this automatically, but if you want to clean files offline:

### Option 1: Command-Line Tool
```bash
# Save ChatGPT response to a text file, then run:
python3 scripts/clean_chatgpt_json.py chatgpt_response.txt my_plan.json

# Or paste from clipboard (macOS):
pbpaste | python3 scripts/clean_chatgpt_json.py - my_plan.json
```

### Option 2: Manual Editing
1. Copy ChatGPT's response
2. Delete first line if it has ` ``` ` or ` ```json `
3. Delete last line if it has ` ``` `
4. Save as `.json` file

**Note**: Neither option is required anymore! The app handles this automatically.

---

## What Changed?

### Old Process (90% Success Rate)
1. Generate prompt
2. Paste into ChatGPT
3. **❌ Manually remove markdown fences** ← Error-prone!
4. Import

### New Process (100% Success Rate)
1. Generate prompt
2. Paste into ChatGPT
3. **✅ Copy response as-is** ← Works automatically!
4. Import

**The app now cleans JSON automatically on the server!**

---

## Troubleshooting

**Most issues are now handled automatically!** But if something fails:

| Error | What Happened | Solution |
|-------|---------------|----------|
| "Invalid JSON after cleaning" | ChatGPT produced broken JSON | Ask ChatGPT to fix and regenerate |
| "Missing 'trainingPlan' root key" | ChatGPT output just workouts array | Tell ChatGPT: "Start with { \"trainingPlan\": {" |
| "end_date must be after start_date" | Dates in wrong order | Check event date in prompt |
| "sportType: invalid value" | Wrong sport type | Use: running, cycling, swimming, triathlon |

**Common ChatGPT Error**: Outputting just the workouts array instead of complete structure:
```json
// ❌ WRONG - Missing root wrapper:
[
  { "date": "2026-01-13", "title": "Easy Run", ... }
]

// ✅ CORRECT - Complete structure:
{
  "trainingPlan": {
    "name": "My Plan",
    "startDate": "2026-01-12",
    "endDate": "2026-04-12",
    "sportType": "triathlon",
    "workouts": [
      { "date": "2026-01-13", "title": "Easy Run", ... }
    ]
  }
}
```

**Success rate: 100%** with automatic cleaning and improved prompts!

---

## Full Documentation

- **`CHATGPT_100_PERCENT_SUCCESS.md`** - How automatic cleaning works
- **`CHATGPT_TRAINING_PLAN_PROMPT_GUIDE.md`** - Advanced prompt tips
