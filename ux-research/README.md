# TrainingPlan UX Research Archive

**Last Updated**: January 3, 2026  
**Research Period**: December 2025 - January 2026  
**Status**: Active Research & Implementation
cd /Users/boetthw3/Documents/99_Other/TrainingPlan
git remote set-url origin https://YOUR_TOKEN@github.com/c0sm0t0m/TrainingPlan.git
git push -u origin main
git remote set-url origin https://github.com/c0sm0t0m/TrainingPlan.git  # Remove token from URL after
---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Competitive Intelligence](#competitive-intelligence)
3. [Strategic Planning](#strategic-planning)
4. [Design Guidelines](#design-guidelines)
5. [Implementation Backlogs](#implementation-backlogs)
6. [TrainingPeaks Reference](#trainingpeaks-reference)
7. [Quick Reference](#quick-reference)

---

## Overview

This directory contains comprehensive UX research conducted to transform TrainingPlan from a basic training platform into a world-class competitor to commercial platforms like TrainingPeaks, TriDot, and TrainerRoad.

**Research Methodology**: Competitive analysis, heuristic evaluation, user flow mapping, feature gap analysis, strategic positioning

**Key Findings**:
- ✅ Can compete on features with platforms charging $240-2,388/year
- ✅ Free + self-hosted = unique market position
- ✅ 30 identified improvements across 4 priority levels
- ✅ Clear differentiation strategy against 4 major competitors

---

## 🔍 Competitive Intelligence

### 1. `UX_COMPETITIVE_ANALYSIS_MATS_TRAINERROAD.md` ⭐ **PRIMARY DOCUMENT**

**Purpose**: Comprehensive competitive analysis of 3 major platforms  
**Competitors Analyzed**: TriDot, TrainerRoad, MATS  
**Date**: January 2-3, 2026  
**Pages**: 35+ pages of detailed analysis

**Key Sections**:
- **Executive Summary**: High-level competitive landscape
- **TriDot Deep Dive**: Premium AI triathlon platform (€348-2,388/year)
  - Physiogenomix genetic optimization
  - EnviroNorm environment adjustment
  - SwimDot/BikeDot/RunDot performance scoring
  - TrainX workout execution scoring
  - RaceX race planning
  - Celebrity endorsements (Mark Allen, Mirinda Carfrae)
- **TrainerRoad Deep Dive**: AI cycling platform ($240/year)
  - Adaptive Training that adjusts to missed workouts
  - AI FTP Detection
  - Career-based progression (Time Crunched → Grand Fondo → Century)
  - TrainNow for ad-hoc workouts
  - Cycling-only limitation
- **MATS Deep Dive**: Archived coaching marketplace
  - Pay-per-service model
  - Coach matching algorithm
  - Subscription pivot (failed)
  - Platform archived in 2023
- **Feature Comparison Matrix**: Side-by-side comparison of all platforms
- **Market Positioning Chart**: Visual price vs features analysis
- **Strategic Recommendations**: 
  - Short-term: "Free TriDot Alternative"
  - Mid-term: Steal best features (simplified)
  - Long-term: Be better than TriDot
- **Implementation Priorities**: Specific features to build

**Use This For**:
- Understanding what competitors offer
- Pricing strategy discussions
- Feature prioritization decisions
- Marketing positioning statements

---

### 2. `TRAININGPEAKS_UX_ANALYSIS.md`

**Purpose**: Detailed analysis of TrainingPeaks (market leader)  
**Date**: December 2025  
**Focus**: UI/UX patterns, workflows, feature inventory

**Key Insights**:
- Manual workout creation workflow
- Calendar-centric interface
- PMC (Performance Management Chart) as killer feature
- Cluttered dashboard with information overload
- Strong but dated UI (needs modernization)

**Use This For**:
- Understanding "industry standard" UX patterns
- Identifying what NOT to copy (cluttered dashboard)
- PMC/TSS implementation reference

---

### 3. `TRAININGPEAKS_UX_REFERENCE.md`

**Purpose**: Quick reference guide to TrainingPeaks features  
**Date**: December 2025  
**Format**: Concise bullet points, screenshots (referenced)

**Sections**:
- Dashboard layout
- Calendar views
- Workout builder
- Activity analysis
- Training zones setup
- Device connections

**Use This For**:
- Quick lookups during implementation
- Feature parity checklist
- UI mockup inspiration

---

### 4. `TRAININGPEAKS_DASHBOARD_WORKOUT_ANALYSIS.md`

**Purpose**: Deep dive into TrainingPeaks dashboard and workout UI  
**Date**: December 2025  
**Focus**: Information hierarchy, metrics display, workout detail views

**Key Findings**:
- Dashboard shows: upcoming workouts, recent activities, CTL/ATL/TSB
- Workout cards use color coding for sport types
- Activity detail includes: map, charts, splits, zones
- Heavy use of tooltips for metric explanations

**Use This For**:
- Dashboard redesign reference
- Workout card component design
- Metrics display patterns

---

## 🎯 Strategic Planning

### 5. `UX_AGENT_STRATEGY.md`

**Purpose**: High-level UX strategy and vision  
**Date**: December 2025  
**Status**: Living document

**Strategic Pillars**:
1. **Simple by Default, Powerful When Needed**
2. **Mobile-First, Desktop-Enhanced**
3. **Data Ownership & Privacy**
4. **Community-Powered Intelligence**
5. **Continuous Iteration**

**Target Personas**:
- **Casual Triathlete**: "I want a plan, not a PhD in exercise science"
- **Data Nerd**: "Show me ALL the metrics and let me analyze them"
- **Former TrainingPeaks User**: "I want TP features without the subscription"
- **Privacy Advocate**: "My training data stays on MY server"

**Use This For**:
- Product vision alignment
- Feature trade-off decisions
- User story writing

---

### 6. `UX_AGENT_SUMMARY.md`

**Purpose**: Executive summary of UX research findings  
**Date**: January 2026  
**Audience**: Quick overview for stakeholders/contributors

**Highlights**:
- 30 improvements identified
- 4 priority levels (P0-P3)
- 10 name proposals ("Tempo" recommended)
- Competitive positioning summary
- Implementation timeline (3 sprints)

**Use This For**:
- Quick project overview
- Onboarding new contributors
- Progress tracking against goals

---

## 🎨 Design Guidelines

### 7. `UX_ANALYSIS.md`

**Purpose**: Initial UX audit and design principles  
**Date**: December 2025  
**Format**: Problem-solution pairs with code examples

**Topics Covered**:
- Navigation patterns (missing back buttons, no breadcrumbs)
- Mobile responsiveness issues
- Empty states (missing or poorly designed)
- Loading states (skeletons vs spinners)
- Error handling patterns
- Accessibility compliance

**Code Examples**:
- ✅ Good: Progressive disclosure, skeleton screens
- ❌ Bad: Information overload, missing navigation

**Use This For**:
- Component design reference
- Code review checklist
- Design system foundation

---

### 8. `UX_IMPROVEMENT_PLAN.md`

**Purpose**: Detailed improvement roadmap with sprints  
**Date**: December 2025  
**Status**: Active development guide

**Sprint Structure**:
- **Sprint 1 (Week 1-2)**: Critical UX fixes (navigation, mobile, empty states)
- **Sprint 2 (Week 3-4)**: Polish & consistency (typography, spacing, colors)
- **Sprint 3 (Week 5-6)**: Advanced features (dark mode, shortcuts, PWA)

**Each Item Includes**:
- Problem description
- Current vs desired state
- TrainingPeaks comparison
- Implementation code
- Effort estimate
- Success metrics

**Use This For**:
- Sprint planning
- Developer task assignments
- Progress tracking

---

### 9. `.github/ux-agent-instructions.md` ⚠️ **LIVES IN .github/**

**Purpose**: Instructions for UX agent (AI assistant)  
**Date**: January 2026  
**Location**: `.github/ux-agent-instructions.md` (NOT in ux-research/)
**Pages**: 8,000+ words

**Sections**:
1. **Mission Statement**: "Make TrainingPlan better than TrainingPeaks"
2. **Design Philosophy**: 15 core principles (simplicity, mobile-first, privacy, etc.)
3. **Analysis Framework**: How to evaluate UX systematically
4. **Competitive Differentiation**: What makes us unique
5. **Output Formats**: How to structure recommendations
6. **Workflow Integration**: When and how to intervene

**Use This For**:
- Configuring AI assistants for UX tasks
- Understanding project design philosophy
- Maintaining consistency across contributors

**Note**: This file stays in `.github/` for GitHub Copilot integration

---

## ✅ Implementation Backlogs

### 10. `UX_AGENT_BACKLOG.md` ⭐ **ACTION ITEMS**

**Purpose**: Prioritized list of 30 UX improvements  
**Date**: January 2026  
**Status**: Active - track completion here

**Priority Levels**:
- **P0 (Critical)**: 4 items - broken UX, must fix ASAP
- **P1 (High)**: 11 items - major improvements, do next
- **P2 (Polish)**: 12 items - nice-to-haves, improve quality
- **P3 (Innovation)**: 3 items - future vision, differentiation

**Format for Each Item**:
```markdown
### #N: [Title] [P0/P1/P2/P3]

**Problem**: Current broken state
**TrainingPeaks**: How they solve it
**Impact**: User frustration level
**Effort**: Time estimate
**Solution**: Implementation approach
**Code**: Specific code changes
```

**Completed Items** (mark with ✅):
- ✅ #8: Remove emoji clutter from branding
- ✅ #29: Remove intrusive welcome message

**Use This For**:
- Daily/weekly development priorities
- Estimating sprint capacity
- Tracking progress (mark ✅ when done)

---

### 11. `UX_AGENT_NAME_PROPOSALS.md`

**Purpose**: Product rebranding research  
**Date**: January 2026  
**Status**: Proposal stage (not implemented)

**Top Recommendations**:
1. **⭐⭐⭐⭐⭐ Tempo** - Recommended (rhythm, pace, modern)
2. ⭐⭐⭐⭐ Stride - Runner-focused
3. ⭐⭐⭐⭐ Apex - Peak performance
4. ⭐⭐⭐ Threshold - Athletic but technical

**Each Name Includes**:
- Concept/meaning
- Pros & cons
- Brand identity mockup
- Tagline suggestions
- Domain availability
- Rating (1-5 stars)

**Implementation Guide**:
- Files to change (3 frontend files)
- Favicon design specs
- Marketing copy updates
- Estimated effort: 1 day

**Use This For**:
- Rebranding decision-making
- Marketing material updates
- Domain registration

---

### 12. `UX_DOCS_README.md`

**Purpose**: Original UX documentation index (deprecated)  
**Date**: December 2025  
**Status**: ⚠️ Replaced by this file (README.md)

**Note**: This file is now redundant. Use `README.md` (this file) instead.

---

## 📖 Quick Reference

### By Task Type

**Need to understand competitors?**
→ `UX_COMPETITIVE_ANALYSIS_MATS_TRAINERROAD.md` (primary)  
→ `TRAININGPEAKS_UX_ANALYSIS.md` (TrainingPeaks deep dive)

**Need to prioritize next features?**
→ `UX_AGENT_BACKLOG.md` (30 items, P0-P3)  
→ `UX_IMPROVEMENT_PLAN.md` (sprint-based roadmap)

**Need design guidance?**
→ `UX_ANALYSIS.md` (patterns + code examples)  
→ `.github/ux-agent-instructions.md` (design philosophy)

**Need to understand project vision?**
→ `UX_AGENT_STRATEGY.md` (strategic pillars)  
→ `UX_AGENT_SUMMARY.md` (executive summary)

**Need TrainingPeaks reference?**
→ `TRAININGPEAKS_UX_REFERENCE.md` (quick lookup)  
→ `TRAININGPEAKS_DASHBOARD_WORKOUT_ANALYSIS.md` (detailed analysis)

**Need to rebrand?**
→ `UX_AGENT_NAME_PROPOSALS.md` (10 name options)

---

### By Urgency

**🔴 Do This Week**:
1. Read `UX_AGENT_BACKLOG.md` items #1-4 (P0 critical)
2. Implement quick wins (2.5 hours total)
3. Fix mobile navigation (#1, #2)

**🟡 Do This Month**:
1. Complete Sprint 1 from `UX_IMPROVEMENT_PLAN.md`
2. Implement P1 items from backlog (#5-15)
3. Consider name rebrand from `UX_AGENT_NAME_PROPOSALS.md`

**🟢 Do This Quarter**:
1. Implement environment adjustment (TriDot competitor feature)
2. Add performance scores (SwimDot/BikeDot/RunDot equivalent)
3. Build workout execution scoring
4. Launch dark mode

---

## 📊 Research Statistics

**Total Documents**: 12 files  
**Total Pages**: 100+ pages of research  
**Competitors Analyzed**: 4 platforms (TriDot, TrainerRoad, TrainingPeaks, MATS)  
**Improvements Identified**: 30 prioritized items  
**Code Examples**: 50+ implementation snippets  
**Effort Estimated**: 6 weeks (3 sprints)

**Research Hours**: ~40 hours  
**Implementation Hours**: ~120 hours (estimated)  
**Potential Annual Savings for Users**: $400-2,600 (vs paid platforms)

---

## 🚀 Getting Started

### For Developers

1. **Read this first**: `README.md` (you're here! ✅)
2. **Understand the vision**: `UX_AGENT_STRATEGY.md`
3. **Pick a task**: `UX_AGENT_BACKLOG.md` (start with P0 items)
4. **Check competitors**: `UX_COMPETITIVE_ANALYSIS_MATS_TRAINERROAD.md`
5. **Follow patterns**: `UX_ANALYSIS.md`

### For Designers

1. **Design philosophy**: `.github/ux-agent-instructions.md`
2. **Current problems**: `UX_AGENT_BACKLOG.md`
3. **Reference UX**: `TRAININGPEAKS_UX_REFERENCE.md`
4. **Brand identity**: `UX_AGENT_NAME_PROPOSALS.md`

### For Product Managers

1. **Executive summary**: `UX_AGENT_SUMMARY.md`
2. **Competitive landscape**: `UX_COMPETITIVE_ANALYSIS_MATS_TRAINERROAD.md`
3. **Roadmap**: `UX_IMPROVEMENT_PLAN.md`
4. **Strategy**: `UX_AGENT_STRATEGY.md`

---

## 📝 Document Maintenance

**Update Frequency**:
- Backlog: Update weekly (mark ✅ for completed items)
- Competitive analysis: Update quarterly (new platforms, pricing changes)
- Strategy: Update semi-annually (product vision evolution)
- Design guidelines: Update as patterns emerge

**Version Control**:
- All documents tracked in Git
- Include date in document header
- Note "Last Updated" in README

**Contributing**:
- Follow existing document structure
- Include code examples where applicable
- Cross-reference related documents
- Update this README when adding new files

---

## 🎯 Success Metrics

**How We'll Know This Research Was Worth It**:

1. **User Metrics** (Target: Q2 2026)
   - Mobile usable: Lighthouse score > 90
   - Page load: < 2 seconds
   - User can create plan: < 5 minutes
   - Navigation clarity: 0 "where do I go?" support requests

2. **Feature Parity** (Target: Q3 2026)
   - ✅ 20/30 backlog items completed
   - ✅ All P0 items fixed
   - ✅ Environment-adjusted workouts (TriDot feature)
   - ✅ Performance scoring (SwimDot/BikeDot/RunDot equivalent)

3. **Competitive Position** (Target: Q4 2026)
   - Match TrainingPeaks on core features
   - Exceed TrainingPeaks on mobile UX
   - Differentiate with self-hosted + free pricing
   - Community-powered AI (unique feature)

---

## 📞 Questions?

**For UX decisions**: Review `.github/ux-agent-instructions.md`  
**For priorities**: Check `UX_AGENT_BACKLOG.md` P0-P3 levels  
**For competitors**: Read `UX_COMPETITIVE_ANALYSIS_MATS_TRAINERROAD.md`  
**For implementation**: Follow `UX_IMPROVEMENT_PLAN.md` sprints

---

**Last Updated**: January 3, 2026  
**Next Review**: January 10, 2026 (weekly backlog update)  
**Document Owner**: UX Research Team
