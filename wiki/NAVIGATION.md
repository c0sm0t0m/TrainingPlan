# Wiki Navigation Guide

This guide explains how to navigate the Kinesis documentation wiki.

## 📂 Directory Structure

```
wiki/
├── Home.md                           # Wiki homepage (start here!)
├── NAVIGATION.md                     # This file
│
├── getting-started/                  # 🎯 Getting Started
│   ├── Quick-Start.md               # → Links to README.md
│   ├── Installation.md              # → Links to LOCAL_DEV_SETUP.md
│   ├── Development-Setup.md         # → Links to LOCAL_DEV_SETUP.md
│   ├── Contributing.md              # → Links to CONTRIBUTING.md
│   └── Developer-Tools.md           # → Links to DEV_AUTO_LOGIN.md, OBS_CODING_SETUP.md
│
├── features/                         # ⚡ Features
│   ├── User-Guides.md               # Index of all user guides
│   ├── AI-Training-Plan.md          # → AI_TRAINING_PLAN_FEATURE.md
│   ├── Trainer-Styles.md            # → TRAINER_STYLES_COMPLETE_GUIDE.md
│   ├── Training-Plan-Activation.md  # → TRAINING_PLAN_ACTIVATION_FEATURE.md
│   ├── Activity-Detail.md           # → ACTIVITY_DETAIL_IMPLEMENTATION_PLAN.md
│   ├── Calendar-Interface.md        # → MOBILE_CALENDAR_OPTION_A_IMPLEMENTATION.md
│   ├── HRV-Tracking.md              # → backend/HRV_IMPLEMENTATION_SUMMARY.md
│   ├── TSS-Calculations.md          # → THRESHOLD_TSS_CALCULATION_AUDIT.md
│   ├── Zone-Calculations.md         # → ZONE_CALCULATION_IMPLEMENTATION.md
│   └── Threshold-Detection.md       # New consolidated doc
│
├── technical/                        # 🔧 Technical Documentation
│   ├── Architecture.md              # New overview doc
│   ├── Tech-Stack.md                # → TECH_STACK.md
│   ├── Database-Schema.md           # New doc (extract from code)
│   ├── API-Documentation.md         # New doc (from backend OpenAPI)
│   ├── Frontend-Implementation.md   # → frontend docs
│   ├── Backend-Implementation.md    # New consolidated backend doc
│   ├── Testing-Strategy.md          # New doc
│   ├── Deployment-Guide.md          # New doc (Docker Compose)
│   ├── Code-Standards.md            # New doc
│   ├── Security.md                  # New doc
│   ├── Performance.md               # New doc
│   └── Troubleshooting.md           # Consolidated troubleshooting
│
├── api-integrations/                 # 🔌 API Integrations
│   ├── Garmin-Overview.md           # → backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md
│   ├── Garmin-Workout-Sync.md       # → backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md
│   ├── Garmin-Activity-Sync.md      # → backend/GARMIN_WORKOUT_SYNC_IMPLEMENTATION.md
│   ├── Garmin-Authentication.md     # → backend/GARMIN_TROUBLESHOOTING.md
│   ├── Garmin-Training-API.md       # → backend/GARMIN_TRAINING_API.md
│   ├── TrainingPeaks.md             # → backend/TRAININGPEAKS_API_RESEARCH.md
│   ├── Strava.md                    # New placeholder doc
│   └── Troubleshooting.md           # Consolidated API troubleshooting
│
└── ux-research/                      # 🎨 UX Research
    ├── Competitive-Landscape.md     # → COMPETITIVE_ANALYSIS.md
    ├── TrainingPeaks-Analysis.md    # → ux-research/competitive_analysis_trainingpeaks.md
    ├── Feature-Comparison.md        # New doc
    ├── UX-Strategy.md               # → ux-research/ux_strategy.md
    ├── Design-Principles.md         # → ux-research/ux_principles.md
    ├── Navigation-Patterns.md       # → ux-research/tp_navigation_patterns.md
    ├── Improvement-Roadmap.md       # → RANKED_IMPROVEMENT_BACKLOG.md
    ├── Research-Archive.md          # → ux-research/research_archive_2025_01.md
    ├── Current-State.md             # → ux-research/current_state_analysis.md
    └── Dashboard-Analysis.md        # → ux-research/dashboard_analysis.md
```

## 🗺️ Navigation Patterns

### 1. Top-Down Navigation
Start at [Home.md](Home.md) → Browse sections → Click into topics

### 2. Search Navigation
Use VS Code search (Cmd/Ctrl + K) → Type keywords → Jump to result

### 3. Cross-References
Follow inline links within documents → Related topics are linked

### 4. Breadcrumb Navigation
Each page shows: `Home > Section > Current Page`

## 🔗 Link Types

### Symbolic Links (Recommended)
Many wiki pages are **symbolic links** to the original documentation:
- Keeps content in one place (no duplication)
- Original files remain in their logical locations
- Wiki provides organized navigation structure

Example:
```bash
# wiki/features/AI-Training-Plan.md → ../../AI_TRAINING_PLAN_FEATURE.md
```

### Standalone Wiki Pages
Some pages exist only in the wiki:
- Index pages (User-Guides.md, Feature-Comparison.md)
- Navigation pages (this file)
- Consolidated pages that merge multiple sources

## 📱 Access Methods

### Method 1: VS Code (Recommended)
1. Open workspace in VS Code
2. Click `wiki/Home.md` in Explorer
3. Use "Open Preview" (Cmd/Shift+V) for rendered view
4. Click links to navigate

### Method 2: File System
1. Open Finder/Explorer
2. Navigate to `TrainingPlan/wiki/`
3. Double-click `Home.md` (opens in default markdown viewer)

### Method 3: Command Line
```bash
cd /Users/boetthw3/Documents/99_Other/TrainingPlan/wiki
open Home.md  # macOS
# or
xdg-open Home.md  # Linux
```

### Method 4: GitHub (if repository is public)
GitHub automatically renders `wiki/` folder as a navigable wiki interface

## 🎯 Quick Navigation Shortcuts

### For New Users
```
wiki/Home.md → Quick Links → Quick Start Guide
```

### For Developers
```
wiki/Home.md → Technical Documentation → Development Setup
```

### For Troubleshooting
```
wiki/Home.md → API Integrations → Troubleshooting
```

### For Feature Documentation
```
wiki/Home.md → Features → [Choose your feature]
```

## 🔍 Finding Specific Topics

| Looking for... | Go to... |
|----------------|----------|
| Setup instructions | `getting-started/Installation.md` |
| How to use AI training plans | `features/AI-Training-Plan.md` |
| Garmin integration issues | `api-integrations/Troubleshooting.md` |
| System architecture | `technical/Architecture.md` |
| UX research findings | `ux-research/` folder |
| Contribution guidelines | `getting-started/Contributing.md` |
| Technology decisions | `technical/Tech-Stack.md` |

## 🔄 Updating the Wiki

When adding new documentation:

1. **Create the markdown file** in the appropriate section
2. **Update Home.md** to link to your new page
3. **Update this NAVIGATION.md** to include the new file
4. **Add cross-references** from related pages

When moving/renaming files:

1. **Update all links** that reference the old path
2. **Update Home.md** navigation
3. **Update this NAVIGATION.md** file structure
4. **Test all links** still work

## 📦 Archive Policy

**Completed features and bug fixes** are moved to `docs/archive/`:
- Preserves historical documentation
- Reduces clutter in active wiki
- Still searchable and accessible

**When to archive:**
- Feature implementation is complete and stable
- Bug has been fixed and verified
- Documentation is no longer actively referenced

## 🆘 Help & Support

**Can't find what you need?**
1. Search this wiki (Cmd/Ctrl + F)
2. Check [Home.md](Home.md) search tips
3. Browse [technical/Troubleshooting.md](technical/Troubleshooting.md)
4. Create a GitHub issue with "documentation" label

---

**Last Updated**: January 7, 2026
