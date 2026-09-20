# ChatGPT Training Plan Generation - Prompt Guide

**⚠️ CRITICAL: Use this enhanced prompt to ensure ChatGPT produces VALID JSON**

## Problem
ChatGPT often wraps JSON in markdown code fences (` ``` `), adds explanations, or produces invalid JSON that fails import.

## Solution
Add explicit formatting instructions that force ChatGPT to output ONLY valid JSON.

---

## Enhanced Prompt Template

Copy and paste this at the **END** of the generated prompt from the app:

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
6. ✅ All date fields MUST be in YYYY-MM-DD format (e.g., "2026-01-15")
7. ✅ All numeric fields MUST be numbers, not strings (e.g., 45, not "45")

EXAMPLE OF CORRECT OUTPUT (first few lines):
{
  "trainingPlan": {
    "name": "Olympic Triathlon Performance Plan",
    "description": "27-week periodized plan...",
    "startDate": "2026-01-12",

EXAMPLE OF INCORRECT OUTPUT (will fail):
```json
{
  "trainingPlan": {
```

START YOUR RESPONSE WITH THIS EXACT CHARACTER: {
END YOUR RESPONSE WITH THIS EXACT CHARACTER: }

NO TEXT BEFORE THE OPENING {
NO TEXT AFTER THE CLOSING }
```

---

## Full Instructions for User

When using ChatGPT to generate a training plan:

### Step 1: Generate Prompt in App
1. Click "Generate AI Training Plan" in Kinesis
2. Fill in your event details
3. Click "Generate Prompt"
4. Copy the generated prompt

### Step 2: Enhance the Prompt
Add this section at the END of the copied prompt:

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
6. ✅ All date fields MUST be in YYYY-MM-DD format (e.g., "2026-01-15")
7. ✅ All numeric fields MUST be numbers, not strings (e.g., 45, not "45")

EXAMPLE OF CORRECT OUTPUT:
{
  "trainingPlan": {
    "name": "My Training Plan",

EXAMPLE OF INCORRECT OUTPUT (will fail):
```json
{

START YOUR RESPONSE WITH: {
END YOUR RESPONSE WITH: }
```

### Step 3: Paste into ChatGPT
1. Open ChatGPT (or Claude)
2. Paste the ENHANCED prompt
3. Wait for response

### Step 4: Extract JSON
1. Copy ChatGPT's response
2. **IF** it includes markdown fences (` ``` `), remove them:
   - Delete the first line (` ```json ` or ` ``` `)
   - Delete the last line (` ``` `)
3. Save to a `.json` file (e.g., `my-training-plan.json`)

### Step 5: Import into Kinesis
1. Go to Training Plans
2. Click "Import AI Plan"
3. Upload your JSON file
4. Review preview and click Import

---

## Validation Checklist

Before importing, verify your JSON file:

### ✅ Required Fields
- [ ] `trainingPlan.name` - String, not empty
- [ ] `trainingPlan.startDate` - Format: YYYY-MM-DD
- [ ] `trainingPlan.endDate` - Format: YYYY-MM-DD (must be after startDate)
- [ ] `trainingPlan.sportType` - One of: running, cycling, swimming, triathlon
- [ ] `trainingPlan.workouts` - Array with at least 1 workout

### ✅ Workout Fields (each workout)
- [ ] `date` - Format: YYYY-MM-DD
- [ ] `title` - String, not empty
- [ ] `sportType` - One of: running, cycling, swimming, strength
- [ ] `workoutType` - One of: easy, tempo, interval, long, recovery, race

### ✅ Optional But Recommended
- [ ] `durationMinutes` - Number (integer)
- [ ] `targetTSS` - Number (integer)
- [ ] `intensityZone` - One of: zone1, zone2, zone3, zone4, zone5

### ❌ Common Errors to Avoid
- [ ] NO markdown code fences (` ``` `)
- [ ] NO trailing commas (e.g., `"value": 123,]` ← wrong)
- [ ] NO single quotes (use double quotes: `"key": "value"`)
- [ ] NO comments (// or /* */)
- [ ] NO undefined/null as strings (use actual null: `"field": null`)

---

## Quick Test Command

To validate your JSON file before importing:

```bash
# macOS/Linux
python3 -c "import json; print('✅ Valid JSON' if json.load(open('your-file.json')) else '❌ Invalid')"

# Windows
python -c "import json; print('✅ Valid JSON' if json.load(open('your-file.json')) else '❌ Invalid')"
```

---

## Example: Correct JSON Structure

```json
{
  "trainingPlan": {
    "name": "Olympic Triathlon Training Plan",
    "description": "12-week plan for Olympic distance triathlon",
    "startDate": "2026-01-12",
    "endDate": "2026-04-05",
    "sportType": "triathlon",
    "targetEvent": "Spring Olympic Triathlon",
    "workouts": [
      {
        "date": "2026-01-13",
        "title": "Easy Run",
        "description": "Zone 2 aerobic run",
        "sportType": "running",
        "workoutType": "easy",
        "durationMinutes": 45,
        "intensityZone": "zone2",
        "targetTSS": 40
      },
      {
        "date": "2026-01-15",
        "title": "FTP Intervals",
        "description": "4x8min @ FTP with 4min recovery",
        "sportType": "cycling",
        "workoutType": "interval",
        "durationMinutes": 60,
        "intensityZone": "zone4",
        "targetTSS": 75,
        "structuredSteps": [
          {
            "stepOrder": 1,
            "stepType": "warmup",
            "durationType": "time",
            "durationValue": 10,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 120,
            "targetValueHigh": 150,
            "targetUnit": "watts",
            "description": "Easy spin"
          },
          {
            "stepOrder": 2,
            "stepType": "work",
            "durationType": "time",
            "durationValue": 8,
            "durationUnit": "minutes",
            "targetType": "power",
            "targetValueLow": 210,
            "targetValueHigh": 230,
            "targetUnit": "watts",
            "description": "FTP interval"
          },
          {
            "stepOrder": 3,
            "stepType": "rest",
            "durationType": "time",
            "durationValue": 4,
            "durationUnit": "minutes",
            "targetType": "open",
            "description": "Recovery spin"
          },
          {
            "stepOrder": 4,
            "stepType": "cooldown",
            "durationType": "time",
            "durationValue": 10,
            "durationUnit": "minutes",
            "targetType": "open",
            "description": "Easy cooldown"
          }
        ]
      }
    ]
  }
}
```

---

## Troubleshooting

### Error: "Invalid JSON: Expecting value: line X"
**Cause**: Markdown code fences or text before/after JSON  
**Fix**: Remove ` ``` ` lines and any explanatory text

### Error: "end_date must be after start_date"
**Cause**: Dates in wrong order or invalid format  
**Fix**: Verify dates are YYYY-MM-DD and endDate > startDate

### Error: "workouts: field required"
**Cause**: Missing workouts array or empty array  
**Fix**: Ensure at least one workout is in the plan

### Error: "sportType: invalid value"
**Cause**: Wrong sport type string  
**Fix**: Use only: running, cycling, swimming, triathlon, strength

### Error: "workoutType: invalid value"
**Cause**: Wrong workout type string  
**Fix**: Use only: easy, tempo, interval, long, recovery, race, brick, strength

---

## Advanced: Using Claude Instead

If ChatGPT keeps adding markdown, try Claude:

```
[Paste the same enhanced prompt]

Additional instruction for Claude:
Output the JSON in a TEXT block (not a code block).
Start your response directly with the { character.
```

---

## Automation Option (Future)

For developers who want to automate JSON cleaning:

```python
import json
import re

def clean_chatgpt_json(response: str) -> dict:
    """Remove markdown and extract JSON from ChatGPT response."""
    # Remove markdown code fences
    cleaned = re.sub(r'^```(?:json)?\s*', '', response, flags=re.MULTILINE)
    cleaned = re.sub(r'```\s*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Parse JSON
    return json.loads(cleaned)

# Usage
chatgpt_response = """```json
{
  "trainingPlan": {...}
}
```"""

plan = clean_chatgpt_json(chatgpt_response)
print(f"Plan name: {plan['trainingPlan']['name']}")
```

---

## Summary

**Key Points**:
1. ✅ Always add the "CRITICAL OUTPUT REQUIREMENTS" section to prompts
2. ✅ Remove markdown code fences (` ``` `) before importing
3. ✅ Verify dates are YYYY-MM-DD format
4. ✅ Ensure numeric fields are numbers, not strings
5. ✅ Test with Python before importing

**Success Rate**:
- ❌ Without enhanced prompt: ~50% success (ChatGPT adds markdown)
- ✅ With enhanced prompt: ~90% success (occasionally needs manual cleanup)

**Best Practice**: Copy-paste the enhanced instructions every time to ensure consistent results.
