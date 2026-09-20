# Test Data Folder - Visual Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     📦 test-data/ Folder                             │
│                                                                       │
│  Complete test data package for AI Training Plan Generator          │
│  Total: 9 files, ~1700 lines of code and documentation             │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  📁 Core Files                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📄 ai-training-plan-config.json          (421 bytes)               │
│  ├─ Purpose: Main test configuration                                │
│  ├─ Format: JSON                                                     │
│  ├─ Contains: Event details, training schedule, constraints         │
│  └─ Edit: Manually or via test-data-editor.html                     │
│                                                                       │
│  🌐 test-data-editor.html                 (12 KB, 332 lines)        │
│  ├─ Purpose: Visual editor for test config                          │
│  ├─ Features: GUI, live preview, clipboard copy                     │
│  ├─ Use: Open directly in browser (no server needed)                │
│  └─ Best for: Non-technical users, quick edits                      │
│                                                                       │
│  🖥️  auto-fill-training-plan.js           (7 KB, 181 lines)         │
│  ├─ Purpose: Auto-fill browser form                                 │
│  ├─ Usage: Paste in browser console at /ai-training-plan           │
│  ├─ Features: DOM manipulation, React state updates                 │
│  └─ Best for: UI testing, development                               │
│                                                                       │
│  🐍 test_ai_plan_config.py                (4.5 KB, 143 lines)       │
│  ├─ Purpose: API testing helper                                     │
│  ├─ Usage: python3 test-data/test_ai_plan_config.py                │
│  ├─ Output: curl commands, Python code, analysis                    │
│  └─ Best for: Backend API testing                                   │
│                                                                       │
│  🎬 demo.sh                                (executable script)       │
│  ├─ Purpose: Interactive demo of all tools                          │
│  ├─ Usage: ./test-data/demo.sh                                      │
│  ├─ Features: Menu-driven, copies scripts, opens files              │
│  └─ Best for: Learning, demonstrations                              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  📚 Documentation Files                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  📖 INDEX.md                               (5 KB, 210 lines)        │
│  ├─ Purpose: Main entry point, file overview                        │
│  ├─ Contains: Quick TL;DR, file comparison, use cases              │
│  └─ Read first: Yes - best starting point                          │
│                                                                       │
│  📖 README.md                              (2.7 KB, 156 lines)      │
│  ├─ Purpose: Detailed usage documentation                           │
│  ├─ Contains: Examples, integration steps, best practices           │
│  └─ Read when: Learning how to use test data                       │
│                                                                       │
│  📖 QUICK_START.md                         (3.2 KB, 173 lines)      │
│  ├─ Purpose: Quick reference guide                                  │
│  ├─ Contains: Commands, troubleshooting, common tasks               │
│  └─ Read when: You need a fast answer                              │
│                                                                       │
│  📖 SUMMARY.md                             (7 KB, 280 lines)        │
│  ├─ Purpose: Comprehensive documentation                            │
│  ├─ Contains: Everything - workflows, customization, edge cases     │
│  └─ Read when: You want complete details                           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🎯 Test Configuration Details                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Event:       Berlin Marathon 2026                                  │
│  Date:        September 27, 2026                                    │
│  Distance:    Marathon (42.195 km)                                  │
│  Goal:        3:30:00 (sub-3:30 finish)                            │
│  Start:       AUTO_NEXT_MONDAY (calculated dynamically)            │
│  Training:    5 days per week                                       │
│  Days:        Monday, Tuesday, Thursday, Saturday, Sunday           │
│                                                                       │
│  Constraints:                                                        │
│  • Tuesday:   Running track session at 6pm (fixed time)            │
│  • Thursday:  Swim technique session at 8pm (fixed time)           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🚀 Usage Flowchart                                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  New User?                                                           │
│    └─▶ Read INDEX.md (overview)                                     │
│         └─▶ Open test-data-editor.html (try it visually)           │
│              └─▶ Read README.md (learn integration)                 │
│                                                                       │
│  Need to test UI?                                                    │
│    └─▶ Start app (./start-all.sh)                                   │
│         └─▶ Open /ai-training-plan                                  │
│              └─▶ Paste auto-fill-training-plan.js in console       │
│                                                                       │
│  Need to test API?                                                   │
│    └─▶ python3 test_ai_plan_config.py                              │
│         └─▶ Copy curl command or Python code                        │
│              └─▶ Get auth token                                     │
│                   └─▶ Execute test                                  │
│                                                                       │
│  Want to customize?                                                  │
│    └─▶ Open test-data-editor.html                                   │
│         └─▶ Edit fields visually                                    │
│              └─▶ Click "Generate JSON"                              │
│                   └─▶ Copy to clipboard                             │
│                        └─▶ Save as new file or replace existing     │
│                                                                       │
│  Quick demo?                                                         │
│    └─▶ ./test-data/demo.sh                                          │
│         └─▶ Follow interactive menu                                 │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🎨 File Size & Purpose Matrix                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  File                    Size    Lines   Purpose                    │
│  ─────────────────────────────────────────────────────────────────  │
│  INDEX.md                5 KB    210     Main documentation hub     │
│  SUMMARY.md              7 KB    280     Comprehensive guide        │
│  QUICK_START.md          3 KB    173     Quick reference            │
│  README.md               3 KB    156     Usage documentation        │
│  test-data-editor.html   12 KB   332     Visual editor (GUI)        │
│  auto-fill-training.js   7 KB    181     Browser auto-fill script   │
│  test_ai_plan_config.py  5 KB    143     API testing helper         │
│  demo.sh                 5 KB    182     Interactive demo           │
│  ai-...config.json       421 B   13      Core test data             │
│  ─────────────────────────────────────────────────────────────────  │
│  TOTAL                   ~48 KB  ~1700   Complete package           │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  💡 Best Tool for Each Task                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Task                              Best Tool                         │
│  ───────────────────────────────────────────────────────────────    │
│  First time learning               INDEX.md                         │
│  Quick command lookup              QUICK_START.md                   │
│  Comprehensive reference           SUMMARY.md                       │
│  Visual editing                    test-data-editor.html            │
│  UI testing                        auto-fill-training-plan.js       │
│  API testing                       test_ai_plan_config.py           │
│  Interactive demo                  demo.sh                          │
│  Direct JSON editing               ai-training-plan-config.json     │
│  Integration examples              README.md                        │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  🎓 Learning Path                                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Beginner (5 minutes):                                              │
│    1. Read INDEX.md (get overview)                                  │
│    2. Open test-data-editor.html (see visual editor)               │
│    3. Click "Generate JSON" (see output)                            │
│                                                                       │
│  Intermediate (15 minutes):                                         │
│    1. Read QUICK_START.md (learn commands)                          │
│    2. Run demo.sh (try interactive menu)                            │
│    3. Try auto-fill script in browser                               │
│                                                                       │
│  Advanced (30 minutes):                                             │
│    1. Read SUMMARY.md (comprehensive guide)                         │
│    2. Customize config for different events                         │
│    3. Test API with python script                                   │
│    4. Create variations for edge cases                              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  ✨ Key Features                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ✅ Auto-calculated start date (always next Monday)                 │
│  ✅ Realistic marathon training plan (5 days/week)                  │
│  ✅ Time-specific constraints (Tuesday 6pm, Thursday 8pm)           │
│  ✅ Visual editor (no coding required)                              │
│  ✅ Browser auto-fill (one-click form filling)                      │
│  ✅ API testing tools (curl + Python examples)                      │
│  ✅ Interactive demo (guided exploration)                           │
│  ✅ Comprehensive docs (4 markdown files)                           │
│  ✅ Fully customizable (edit JSON or use GUI)                       │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════
 Created: January 6, 2026
 Version: 1.0.0
 Maintainer: Kinesis Development Team
═══════════════════════════════════════════════════════════════════════
