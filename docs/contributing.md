# Contributing

Thanks for contributing. This repository contains both backend and frontend code, but changes should keep the Django REST API consistent with the documented behavior.

## Setup

Follow the setup steps in [README.md](../README.md).

## Development Workflow

1. Create a feature branch.
2. Make changes with tests where appropriate.
3. Update documentation when behavior or configuration changes.

## Tests

Backend tests:

```bash
cd backend
python manage.py test
```

Frontend tests (if applicable):

```bash
cd frontend
npm test
```

## Pull Requests

- Use clear descriptions and scope.
- Avoid unrelated formatting changes.
- Ensure documentation stays accurate.