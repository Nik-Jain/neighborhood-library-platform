# Contributing Guidelines

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/neighborhood-library-platform.git
   cd neighborhood-library-platform
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Code Style

### Python

```bash
# Format with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

### JavaScript/TypeScript

```bash
# Format with Prettier
npm run prettier

# Lint with ESLint
npm run lint
```

## Commit Messages

Follow conventional commits:

```
feat: Add new feature
fix: Fix a bug
docs: Update documentation
style: Code style changes
refactor: Refactor code
test: Add or update tests
chore: Dependencies and build changes
```

Example:
```
feat(members): Add member suspension functionality

- Add suspend and activate endpoints
- Update member status validation
- Add tests for member status changes
```

## Pull Request Process

1. **Write tests** for new features
2. **Run linting and formatting**
3. **Update documentation**
4. **Create PR with clear description**
5. **Request review** from maintainers
6. **Address feedback** and update PR
7. **Squash commits** if requested

## Testing

### Run Tests

```bash
# Backend
python manage.py test

# Frontend
npm test
```

### Coverage

```bash
# Backend
pytest --cov=library_service --cov-report=html
```

## Documentation

Update documentation for:
- New API endpoints
- Database schema changes
- Configuration options
- Deployment procedures

## Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] No breaking changes
- [ ] Performance implications considered
- [ ] Security concerns addressed
- [ ] Error handling is appropriate

## Questions?

- Open an issue for bugs
- Discuss features in discussions
- Contact maintainers for help

Thank you for contributing!
