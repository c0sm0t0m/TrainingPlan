# Test Data for Kinesis AI Training Plan Generator

## 📦 Complete Test Data Package

This folder contains pre-configured test data and tools for the **AI Training Plan Generator** feature.

### 🎯 Purpose

Automatically fill the "Configure Training Plan" UI with realistic test data including:
- Event details (Berlin Marathon 2026)
- Training schedule (5 days/week starting next Monday)
- Time constraints (Tuesday track @ 6pm, Thursday swim @ 8pm)

---

## 📁 Files Overview

| File | Purpose | Size | Use When |
|------|---------|------|----------|
| **ai-training-plan-config.json** | Core test configuration | 421B | Need raw JSON data |
| **test-data-editor.html** | Visual editor | 12KB | Want GUI to edit config |
| **auto-fill-training-plan.js** | Browser auto-fill script | 7KB | Testing frontend UI |
| **test_ai_plan_config.py** | API testing helper | 4.5KB | Testing backend API |
| **SUMMARY.md** | Complete documentation | 7KB | Need full details |
| **QUICK_START.md** | Quick reference | 3.2KB | Need fast answer |
| **README.md** | Main documentation | 2.7KB | Getting started |

---

## 🚀 Quick Start (Choose One)

### 🎨 Option 1: Visual Editor (Recommended)
```bash
open test-data/test-data-editor.html
```
- Easiest method - no coding required
- Edit fields visually
- See live preview
- Copy JSON to clipboard
- Works offline

### 🌐 Option 2: Browser Auto-Fill
```bash
# 1. Start app
./start-all.sh

# 2. Open http://localhost:5173/ai-training-plan

# 3. Press F12 (DevTools)

# 4. Paste contents of auto-fill-training-plan.js
```
- Fastest for UI testing
- Fills form automatically
- Works on all steps

### 🐍 Option 3: API Testing
```bash
python3 test-data/test_ai_plan_config.py
```
- Best for backend testing
- Generates curl commands
- Shows analysis
- Provides Python code

### ✏️ Option 4: Direct JSON Edit
```bash
code test-data/ai-training-plan-config.json
```
- Most flexible
- Full control
- For advanced users

---

## 📋 Default Test Configuration

```json
{
  "eventName": "Berlin Marathon 2026",
  "eventDate": "2026-09-27",
  "eventDistance": "Marathon (42.195 km)",
  "goalTime": "3:30:00",
  "startDate": "AUTO_NEXT_MONDAY",
  "trainingDaysPerWeek": 5,
  "preferredTrainingDays": [
    "monday",
    "tuesday",
    "thursday",
    "saturday",
    "sunday"
  ],
  "additionalNotes": "Tuesdays: Running track session at 6 pm always\nThursdays: 8pm swim technique session."
}
```

**Key Features:**
- ✅ Start date automatically set to next Monday
- ✅ Realistic marathon goal (sub-3:30)
- ✅ 5-day training week (balanced)
- ✅ Fixed time constraints (track & swim)
- ✅ ~36 weeks training period

---

## 📖 Documentation Structure

### For Quick Reference
- **QUICK_START.md** - Common commands, troubleshooting, tips
- Use when: You know what you want, need syntax

### For Learning
- **README.md** - Usage instructions, examples, integration
- Use when: First time using test data

### For Complete Details
- **SUMMARY.md** - Everything: workflows, customization, edge cases
- Use when: Need comprehensive information

### For Visual Editing
- **test-data-editor.html** - Interactive GUI
- Use when: Want to see/edit data visually

---

## 🎯 Use Cases

### UI Development
```bash
# Auto-fill form while developing
open http://localhost:5173/ai-training-plan
# Paste auto-fill-training-plan.js in console
```

### API Testing
```bash
# Generate test requests
python3 test-data/test_ai_plan_config.py
# Copy curl command
```

### Creating Variations
```bash
# Visual editing
open test-data-editor.html
# Adjust fields, copy JSON
```

### Documentation/Demos
```bash
# Show example configuration
cat ai-training-plan-config.json
```

---

## 🔧 Customization Examples

### Different Events

**Half Marathon:**
```json
{
  "eventName": "City Half Marathon",
  "eventDistance": "Half Marathon (21.097 km)",
  "goalTime": "1:45:00",
  "trainingDaysPerWeek": 4
}
```

**10K Race:**
```json
{
  "eventName": "Parkrun Challenge",
  "eventDistance": "10K",
  "goalTime": "00:45:00",
  "trainingDaysPerWeek": 4
}
```

### Different Schedules

**Weekend Warrior:**
```json
{
  "trainingDaysPerWeek": 3,
  "preferredTrainingDays": ["friday", "saturday", "sunday"]
}
```

**Daily Trainer:**
```json
{
  "trainingDaysPerWeek": 6,
  "preferredTrainingDays": ["monday", "tuesday", "wednesday", "thursday", "saturday", "sunday"]
}
```

---

## 🐛 Common Issues

### Auto-fill not working?
- ✅ Check you're on `/ai-training-plan` page
- ✅ Ensure step 0 or 1 is active
- ✅ Look for console errors (F12)

### Python script fails?
- ✅ Use `python3` not `python`
- ✅ Run from project root
- ✅ Check JSON file exists

### HTML editor broken?
- ✅ Try different browser
- ✅ Check JavaScript console
- ✅ Clear cache

---

## 📚 Learn More

| Topic | File | Time |
|-------|------|------|
| Quick commands | QUICK_START.md | 5 min |
| Basic usage | README.md | 10 min |
| Full guide | SUMMARY.md | 20 min |
| Visual editing | test-data-editor.html | 2 min |
| API testing | Run python script | 1 min |

---

## ⚡ TL;DR

```bash
# 1. Open visual editor
open test-data/test-data-editor.html

# 2. Or auto-fill browser form
# Paste auto-fill-training-plan.js in console at /ai-training-plan

# 3. Or test API
python3 test-data/test_ai_plan_config.py
```

**Default test case:**
- Berlin Marathon 2026 (Sep 27)
- Goal: 3:30:00 (sub-3:30)
- Start: Next Monday
- 5 days/week (Mon, Tue, Thu, Sat, Sun)
- Tuesday: Track @ 6pm
- Thursday: Swim @ 8pm

---

**Created:** January 6, 2026  
**Version:** 1.0.0  
**Maintainer:** Kinesis Development Team
