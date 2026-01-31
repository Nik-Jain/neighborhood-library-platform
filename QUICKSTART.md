# Installation & Quick Start Guide

## System Requirements

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- PostgreSQL 15 (for local development)

## Quick Start (Docker - Recommended)

### 1. Clone Repository
```bash
git clone <repository-url>
cd neighborhood-library-platform
```

### 2. Run Setup Script
```bash
chmod +x start.sh
bash start.sh
```

This script will:
- Create `.env` file
- Build Docker images
- Start all services
- Run migrations
- Create superuser
- Seed database with sample data

### 3. Access the Application

| Component | URL | Credentials |
|-----------|-----|-------------|
| Frontend | http://localhost:3000 | N/A |
| API | http://localhost:8000/api/v1 | See below |
| API Docs | http://localhost:8000/api/docs/ | N/A |
| Admin Panel | http://localhost:8000/admin/ | admin / admin123 |

## Local Development Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Create .env file in project root
cd ..
cp .env.example .env

# Configure database in .env
# DB_HOST=localhost (instead of postgres)
# DB_NAME=neighborhood_library
# DB_USER=postgres
# DB_PASSWORD=postgres

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database
python manage.py seed_database

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
# In a new terminal
cd frontend

# Install dependencies
npm install

# Create .env.local (optional, defaults are fine)
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev

# Access at http://localhost:3000
```

## Database Setup (Local PostgreSQL)

If using local PostgreSQL instead of Docker:

```bash
# Create database
createdb neighborhood_library

# Create user
createuser -P postgres

# Connect and verify
psql -U postgres -d neighborhood_library
```

Then update `.env`:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=neighborhood_library
DB_USER=postgres
DB_PASSWORD=<your-password>
```

## Testing

### Run Backend Tests
```bash
cd backend
python manage.py test library_service.apps.core

# With coverage
pytest --cov=library_service --cov-report=html
```

### Run Frontend Tests
```bash
cd frontend
npm test
```

## Useful Commands

### Docker Commands
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f api

# Run Django command
docker-compose exec api python manage.py <command>

# Access database
docker-compose exec postgres psql -U postgres -d neighborhood_library

# Rebuild images
docker-compose build --no-cache
```

### Django Commands
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database
python manage.py seed_database

# Create migration
python manage.py makemigrations

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic

# Reset database (WARNING: deletes all data)
python manage.py flush
```

### Frontend Commands
```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Run tests
npm test
```

## API Authentication

### Get Token

1. **Via Admin Panel:**
   - Go to http://localhost:8000/admin/
   - Create a user
   - Go to Tokens section (if visible)

2. **Via Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api-token-auth/',
    json={'username': 'admin', 'password': 'admin123'}
)
token = response.json()['token']
print(token)
```

3. **Via cURL:**
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Use Token in Requests

```bash
curl -H "Authorization: Token <your-token>" \
  http://localhost:8000/api/v1/members/
```

## First Steps

1. **Access Admin Panel** (http://localhost:8000/admin/)
   - Create a test member
   - Add some books
   - Create borrowing records

2. **Explore API** (http://localhost:8000/api/docs/)
   - Try API endpoints
   - Review request/response formats
   - Test different operations

3. **Use Frontend** (http://localhost:3000)
   - View dashboard
   - Manage members and books
   - Track borrowings

## Troubleshooting

### Port Already in Use
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9

# Kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

### Database Connection Error
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### CORS Errors
Update `CORS_ALLOWED_ORIGINS` in .env:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Module Not Found
```bash
# Reinstall requirements
pip install -r requirements.txt

# For frontend
npm install
```

## Development Workflow

### Adding a New Feature

1. **Backend:**
   ```bash
   cd backend
   # Create model changes
   python manage.py makemigrations
   python manage.py migrate
   # Update serializers and views
   # Write tests
   python manage.py test
   ```

2. **Frontend:**
   ```bash
   cd frontend
   # Create components
   # Add API calls
   npm test
   ```

3. **Testing:**
   ```bash
   # Test locally
   # Test in Docker
   docker-compose up -d
   docker-compose exec api pytest
   ```

## Deployment

For production deployment, see [DEPLOYMENT_GUIDE.md](./docs/DEPLOYMENT_GUIDE.md)

## Support

- Check [FAQ](./docs/FAQ.md) for common questions
- Review [ARCHITECTURE.md](./docs/ARCHITECTURE.md) for design details
- See [API_REFERENCE.md](./docs/API_REFERENCE.md) for endpoint details
- Read [CONTRIBUTING.md](./docs/CONTRIBUTING.md) to contribute

## Next Steps

1. ✅ Application is running
2. 📚 Review the documentation
3. 🧪 Run the tests
4. 🚀 Explore the API
5. 💻 Extend with new features
6. 📦 Deploy to production

Happy coding! 🎉
