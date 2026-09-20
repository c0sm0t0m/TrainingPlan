# Contributing to Kinesis

Thank you for your interest in contributing to Kinesis! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose
- Git

### Getting Started

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/trainingplan.git
   cd trainingplan
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Install dependencies**
   
   Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   
   Frontend:
   ```bash
   cd frontend
   npm install
   ```

## Development Workflow

### Branching Strategy
- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes
- `hotfix/*` - Emergency fixes

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Commit your changes**
   Use conventional commits:
   ```bash
   git commit -m "feat: add garmin activity sync"
   git commit -m "fix: correct TSS calculation"
   git commit -m "docs: update API documentation"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for function signatures
- Write docstrings for modules, classes, and functions
- Use Ruff for linting and formatting
- Maximum line length: 100 characters

Example:
```python
from typing import List, Optional

async def get_activities(
    user_id: int,
    sport_type: Optional[str] = None,
    limit: int = 50
) -> List[Activity]:
    """
    Retrieve activities for a user.
    
    Args:
        user_id: The ID of the user
        sport_type: Optional filter by sport type
        limit: Maximum number of activities to return
        
    Returns:
        List of Activity objects
    """
    # Implementation
    pass
```

### TypeScript (Frontend)
- Use TypeScript strict mode
- Define interfaces for all data structures
- Use functional components with hooks
- Follow React best practices
- Use ESLint and Prettier

Example:
```typescript
interface Activity {
  id: number;
  name: string;
  sport_type: string;
  distance: number;
  duration: number;
}

const ActivityList: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  
  useEffect(() => {
    // Fetch activities
  }, []);
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

## Testing

### Backend Testing
- Write unit tests for services and utilities
- Write integration tests for API endpoints
- Use pytest fixtures for test data
- Aim for >80% code coverage

```python
import pytest
from src.services.training_load import calculate_tss

def test_calculate_tss_running():
    """Test TSS calculation for running activities."""
    result = calculate_tss(
        duration_seconds=3600,
        normalized_pace=300,  # 5:00/km
        threshold_pace=270,   # 4:30/km
    )
    assert result > 0
    assert result < 200
```

### Frontend Testing
- Write unit tests for utilities
- Write component tests with React Testing Library
- Test user interactions and edge cases

```typescript
import { render, screen } from '@testing-library/react';
import ActivityCard from './ActivityCard';

test('renders activity name', () => {
  const activity = {
    id: 1,
    name: 'Morning Run',
    sport_type: 'running',
    distance: 5000,
    duration: 1800,
  };
  
  render(<ActivityCard activity={activity} />);
  expect(screen.getByText('Morning Run')).toBeInTheDocument();
});
```

## Documentation

### Code Documentation
- Document all public APIs
- Include usage examples
- Explain complex algorithms
- Keep comments up to date

### API Documentation
- FastAPI automatically generates OpenAPI docs
- Add descriptions to route decorators
- Document request/response models

```python
@router.post("/activities", response_model=Activity)
async def create_activity(
    activity: ActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> Activity:
    """
    Create a new activity.
    
    This endpoint creates a new activity record for the authenticated user.
    The activity can be manually entered or imported from external services.
    
    - **name**: Activity name (e.g., "Morning Run")
    - **sport_type**: One of: running, cycling, swimming
    - **distance**: Distance in meters
    - **duration**: Duration in seconds
    """
    # Implementation
    pass
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new functionality
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Request review** from maintainers

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Commit messages follow conventional commits
- [ ] No merge conflicts
- [ ] Reviewed own code

## Issue Reporting

### Bug Reports
Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python/Node version)
- Screenshots if applicable

### Feature Requests
Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Mockups or examples (optional)

## Code Review Guidelines

### As a Reviewer
- Be constructive and respectful
- Explain reasoning for requested changes
- Approve when satisfied
- Don't block on minor style issues

### As an Author
- Respond to all comments
- Make requested changes or discuss alternatives
- Keep PRs focused and reasonably sized
- Be open to feedback

## Release Process

1. Update version in `package.json` and `__init__.py`
2. Update CHANGELOG.md
3. Create release tag: `git tag -a v0.2.0 -m "Release v0.2.0"`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release with changelog

## Questions?

- Open an issue for questions
- Refer to documentation in `/docs`
- Check existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
