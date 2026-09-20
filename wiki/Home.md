# Kinesis Wiki - Documentation Hub

**Kinesis** (κίνησις): Transform your training potential into kinetic performance.

Welcome to the Kinesis documentation wiki! This is your central hub for all project documentation, organized for easy navigation.

---

## 🚀 Quick Links

### For New Users
- [**Quick Start Guide**](getting-started/Quick-Start.md) - Get up and running in 5 minutes
- [**Installation**](getting-started/Installation.md) - Detailed setup instructions
- [**User Guides**](features/User-Guides.md) - How to use key features

### For Developers
- [**Development Setup**](getting-started/Development-Setup.md) - Local development environment
- [**Contributing**](getting-started/Contributing.md) - How to contribute to the project
- [**Architecture Overview**](technical/Architecture.md) - System design and technology stack

### For Troubleshooting
- [**Common Issues**](technical/Troubleshooting.md) - Solutions to frequently encountered problems
- [**API Integration Issues**](api-integrations/Troubleshooting.md) - Garmin, TrainingPeaks, Strava issues

---

## 📚 Documentation Sections

### 🎯 [Getting Started](getting-started/)
Essential guides to get you up and running with Kinesis.

- [Quick Start Guide](getting-started/Quick-Start.md) - 5-minute setup
- [Installation](getting-started/Installation.md) - Complete installation guide
- [Development Setup](getting-started/Development-Setup.md) - Local dev environment
- [Contributing](getting-started/Contributing.md) - Contribution guidelines
- [Developer Tools](getting-started/Developer-Tools.md) - Useful dev tools

---

### ⚡ [Features](features/)
Documentation for all Kinesis features and capabilities.

#### Core Features
- [AI Training Plan Generator](features/AI-Training-Plan.md) - Generate personalized training plans with AI
- [Trainer Styles](features/Trainer-Styles.md) - 17+ coaching personalities to choose from
- [Training Plan Activation](features/Training-Plan-Activation.md) - One-click plan activation system
- [Activity Detail Views](features/Activity-Detail.md) - Comprehensive activity analysis
- [Calendar Interface](features/Calendar-Interface.md) - Mobile-optimized weekly/monthly views

#### Analytics & Metrics
- [HRV Tracking](features/HRV-Tracking.md) - Heart Rate Variability monitoring
- [TSS Calculations](features/TSS-Calculations.md) - Training Stress Score methodology
- [Zone Calculations](features/Zone-Calculations.md) - Power, heart rate, and pace zones
- [Threshold Detection](features/Threshold-Detection.md) - Automatic FTP/threshold updates

---

### 🔧 [Technical Documentation](technical/)
Architecture, implementation details, and technical references.

#### System Architecture
- [Architecture Overview](technical/Architecture.md) - High-level system design
- [Technology Stack](technical/Tech-Stack.md) - Technologies, frameworks, and rationale
- [Database Schema](technical/Database-Schema.md) - Data models and relationships
- [API Documentation](technical/API-Documentation.md) - REST API reference

#### Implementation Guides
- [Frontend Implementation](technical/Frontend-Implementation.md) - React/TypeScript architecture
- [Backend Implementation](technical/Backend-Implementation.md) - FastAPI/Python architecture
- [Testing Strategy](technical/Testing-Strategy.md) - Unit, integration, and E2E tests
- [Deployment Guide](technical/Deployment-Guide.md) - Production deployment on QNAP NAS

#### Best Practices
- [Code Standards](technical/Code-Standards.md) - Coding conventions and style guide
- [Security Practices](technical/Security.md) - Authentication, authorization, data protection
- [Performance Optimization](technical/Performance.md) - Caching, queries, bundle optimization
- [Troubleshooting](technical/Troubleshooting.md) - Common issues and solutions

---

### 🔌 [API Integrations](api-integrations/)
Third-party service integrations and API documentation.

#### Garmin Connect
- [Garmin Integration Overview](api-integrations/Garmin-Overview.md) - Complete integration guide
- [Garmin Workout Sync](api-integrations/Garmin-Workout-Sync.md) - Upload workouts to Garmin
- [Garmin Activity Sync](api-integrations/Garmin-Activity-Sync.md) - Import activities from Garmin
- [Garmin Authentication](api-integrations/Garmin-Authentication.md) - OAuth setup and troubleshooting
- [Garmin Training API](api-integrations/Garmin-Training-API.md) - Official Training API research

#### Other Platforms
- [TrainingPeaks Integration](api-integrations/TrainingPeaks.md) - TrainingPeaks API integration
- [Strava Integration](api-integrations/Strava.md) - Strava API integration (planned)

#### Troubleshooting
- [API Troubleshooting Guide](api-integrations/Troubleshooting.md) - Common API issues and solutions

---

### 🎨 [UX Research](ux-research/)
User experience research, competitive analysis, and design decisions.

#### Competitive Analysis
- [TrainingPeaks Analysis](ux-research/TrainingPeaks-Analysis.md) - Strengths and weaknesses
- [Competitive Landscape](ux-research/Competitive-Landscape.md) - Market analysis
- [Feature Comparison](ux-research/Feature-Comparison.md) - How we stack up

#### UX Strategy
- [UX Strategy Document](ux-research/UX-Strategy.md) - Overall UX approach
- [Design Principles](ux-research/Design-Principles.md) - Core design philosophy
- [Navigation Patterns](ux-research/Navigation-Patterns.md) - Learned from TrainingPeaks
- [Improvement Roadmap](ux-research/Improvement-Roadmap.md) - Prioritized UX backlog

#### Research Findings
- [User Research Archive](ux-research/Research-Archive.md) - Historical research findings
- [Current State Analysis](ux-research/Current-State.md) - Where we are today
- [Dashboard Analysis](ux-research/Dashboard-Analysis.md) - Dashboard UX research

---

## 📖 Documentation Map

### By Audience

**🆕 New Users**
1. Start: [Quick Start Guide](getting-started/Quick-Start.md)
2. Learn: [AI Training Plan User Guide](features/AI-Training-Plan.md#user-guide)
3. Explore: [Trainer Styles Guide](features/Trainer-Styles.md#user-guide)

**👨‍💻 Developers**
1. Setup: [Development Setup](getting-started/Development-Setup.md)
2. Architecture: [Tech Stack](technical/Tech-Stack.md)
3. Contribute: [Contributing Guide](getting-started/Contributing.md)

**🔧 DevOps/Admins**
1. Deploy: [Deployment Guide](technical/Deployment-Guide.md)
2. Monitor: [Performance Guide](technical/Performance.md)
3. Secure: [Security Best Practices](technical/Security.md)

**🎨 UX/Product**
1. Research: [Competitive Analysis](ux-research/Competitive-Landscape.md)
2. Strategy: [UX Strategy](ux-research/UX-Strategy.md)
3. Roadmap: [Improvement Backlog](ux-research/Improvement-Roadmap.md)

---

## 🔍 Search Tips

**Finding what you need:**
- Use the search bar (Cmd/Ctrl + K in VS Code)
- Check the relevant section above
- Browse by audience type
- Check [Troubleshooting](technical/Troubleshooting.md) for common issues

**Common searches:**
- "How do I set up development environment?" → [Development Setup](getting-started/Development-Setup.md)
- "How do I generate an AI training plan?" → [AI Training Plan Feature](features/AI-Training-Plan.md)
- "Why isn't Garmin syncing?" → [Garmin Troubleshooting](api-integrations/Garmin-Authentication.md#troubleshooting)
- "How do TSS calculations work?" → [TSS Calculations](features/TSS-Calculations.md)
- "What trainer styles are available?" → [Trainer Styles](features/Trainer-Styles.md)

---

## 🔄 Recent Updates

See [CHANGELOG.md](../CHANGELOG.md) for detailed version history.

**Latest Features:**
- ✅ AI Training Plan Generator with 17+ trainer styles
- ✅ HRV (Heart Rate Variability) tracking and sync
- ✅ Training Plan Activation system
- ✅ Mobile-optimized calendar interface
- ✅ Automatic threshold detection from activities
- ✅ Comprehensive activity detail views

---

## 📝 Contributing to Documentation

Found something unclear? Want to add documentation?

1. Read the [Contributing Guide](getting-started/Contributing.md)
2. Create a new markdown file in the appropriate wiki section
3. Update this Home.md to link to your new page
4. Submit a pull request

**Documentation standards:**
- Use clear, concise language
- Include code examples where relevant
- Add screenshots for UI features
- Link to related pages
- Keep it up to date

---

## 🆘 Need Help?

**Can't find what you're looking for?**
1. Check [Troubleshooting Guide](technical/Troubleshooting.md)
2. Search this wiki (Cmd/Ctrl + K)
3. Check [GitHub Issues](https://github.com/yourusername/kinesis/issues)
4. Review [API Integration Issues](api-integrations/Troubleshooting.md)

**Still stuck?**
- Create a GitHub issue with the "documentation" label
- Include what you were looking for and where you expected to find it

---

## 📚 Archive

Completed features and historical documentation have been moved to `docs/archive/`:
- [Completed Features Archive](../docs/archive/completed-features/)
- [Bug Fix Archive](../docs/archive/bug-fixes/)

These are preserved for historical reference but are no longer actively maintained.

---

**Last Updated**: January 7, 2026  
**Wiki Version**: 1.0  
**Project Version**: See [CHANGELOG.md](../CHANGELOG.md)
