# Neighborhood Library Platform (Backend)

Production-grade Django REST API for a neighborhood library system. Provides role-based access control, token authentication, and CRUD workflows for members, books, borrowings, and fines.

## Documentation

- Architecture: [docs/architecture.md](docs/architecture.md)
- API reference: [docs/api.md](docs/api.md)
- Contributing: [docs/contributing.md](docs/contributing.md)

## Quick Start (Docker)

### Option A: Scripted setup (recommended)

```bash
cp .env.example .env
./start.sh
```

### Option B: Manual Docker Compose

```bash
cp .env.example .env
docker-compose up -d --build
```

### Access points

- API: http://localhost:8000/api/v1
- API docs (Swagger): http://localhost:8000/api/docs/
- OpenAPI schema: http://localhost:8000/api/schema/
- Admin: http://localhost:8000/admin/
- Health check: http://localhost:8000/api/health/

## Local Development (Backend)

```bash
cp .env.example .env
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python manage.py migrate
python manage.py bootstrap_roles
python manage.py createsuperuser
python manage.py runserver
```

### Optional: seed sample data

```bash
cd backend
python manage.py seed_database
```

## Frontend (Optional)

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
```

## Environment Configuration

All configuration is driven by .env. Copy from .env.example and update as needed.

Key variables:

- DEBUG
- SECRET_KEY
- ALLOWED_HOSTS
- DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
- CORS_ALLOWED_ORIGINS
- NEXT_PUBLIC_API_URL
- API_PORT, FRONTEND_PORT, NGINX_PORT
- DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD

## Authentication

This API uses token authentication. Obtain a token via signup or login:

- POST /api/v1/auth/signup/
- POST /api/v1/auth/login/

Include the token in requests:

```
Authorization: Token <token>
```

Legacy endpoint (email + password):

- POST /api-token-auth/

## Production Deployment

```bash
cp .env.example .env
# Update .env with production values
./start-prod.sh
```

Alternatively, run the production compose file directly:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

To enable Nginx in the standard compose file:

```bash
docker-compose --profile production up -d
```

## Testing

```bash
cd backend
python manage.py test
```

---

If you are looking for API details, go to [docs/api.md](docs/api.md).# Neighborhood Library Platform

A comprehensive library management system built with Django REST Framework and Next.js, featuring role-based access control (RBAC) and full CRUD operations for books, members, borrowings, and fines.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR Python 3.12+ and Node.js 18+ for local development

### One-Command Deployment

```bash
# Clone the repository
git clone <repository-url>
cd neighborhood-library-platform

# Copy environment configuration
cp .env.example .env

# Edit .env with your settings (optional for development)
nano .env  # or use your preferred editor

# Start all services
docker-compose up -d

# Wait for services to be ready (takes ~30 seconds)
# Access the application:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000/api/v1
# - Admin Panel: http://localhost:8000/admin
```

### Production Deployment with Nginx

```bash
# Start with nginx reverse proxy
docker-compose --profile production up -d

# Access via Nginx:
# - Application: http://localhost (port 80)
# - API through proxy: http://localhost/api
# - Static files served by Nginx
```

## 📋 Features

- **User Management**: Registration, authentication, and role-based access control
- **Book Management**: CRUD operations for books with search and filtering
- **Member Management**: Manage library members and their profiles
- **Borrowing System**: Track book loans with due dates and returns
- **Fine Management**: Automated fine calculation and payment tracking
- **Admin Dashboard**: Comprehensive admin interface for librarians
- **RESTful API**: Well-documented API with OpenAPI/Swagger support
- **Security**: Token-based authentication, permission controls, rate limiting

## 🏗️ Architecture

### Technology Stack

**Backend:**
- Django 4.2.8
- Django REST Framework 3.14.0
- PostgreSQL 15
- Gunicorn (WSGI server)

**Frontend:**
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- Zustand (State Management)

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Production reverse proxy)
- PostgreSQL (Database)

### System Design

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Nginx     │─────▶│  Frontend    │─────▶│  Backend    │
│  (Proxy)    │      │  (Next.js)   │      │  (Django)   │
└─────────────┘      └──────────────┘      └─────────────┘
                                                    │
                                            ┌───────▼────────┐
                                            │   PostgreSQL   │
                                            └────────────────┘
```

## 🔧 Configuration

### Environment Variables

The `.env.example` file contains all configurable options. Key variables:

```bash
# Security
DEBUG=False  # Set to False in production!
SECRET_KEY=your-secret-key-here  # Generate a strong key

# Database
DB_NAME=neighborhood_library
DB_USER=postgres
DB_PASSWORD=secure-password  # Change in production!
DB_HOST=postgres
DB_PORT=5432

# API
ALLOWED_HOSTS=localhost,yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Ports
API_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
```

### Generating a Secure Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🐳 Docker Deployment

### Services

The application runs in multiple Docker containers:

1. **postgres**: PostgreSQL database
2. **api**: Django REST API backend
3. **frontend**: Next.js frontend application
4. **nginx**: Reverse proxy (production only)

### Common Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f api  # Specific service

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Execute commands in containers
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py createsuperuser
docker-compose exec postgres psql -U postgres -d neighborhood_library

# Check service health
docker-compose ps
```

### Data Persistence

Data is persisted in Docker volumes:
- `postgres_data`: Database data
- `static_volume`: Django static files
- `media_volume`: User-uploaded media

### Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres neighborhood_library > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres neighborhood_library < backup.sql

# Backup volumes
docker run --rm -v neighborhood-library-platform_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 🛠️ Local Development

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Set up database (PostgreSQL required)
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run development server
npm run dev
```

## 📚 API Documentation

Once running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/
- **ReDoc**: http://localhost:8000/api/schema/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🧪 Testing

```bash
# Backend tests
docker-compose exec api python manage.py test

# With coverage
docker-compose exec api pytest --cov=. --cov-report=html

# Frontend tests
cd frontend && npm test
```

## 👥 Default Users

After initial setup, default superuser credentials (if configured in .env):

- **Username**: admin (or value from DJANGO_SUPERUSER_USERNAME)
- **Password**: admin123 (or value from DJANGO_SUPERUSER_PASSWORD)

**⚠️ Change these credentials immediately in production!**

## 🔒 Security Considerations

### For Production Deployment

1. **Environment Variables**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Update `ALLOWED_HOSTS` with your domain
   - Use secure database credentials

2. **HTTPS**:
   - Enable SSL/TLS certificates
   - Update `NEXT_PUBLIC_API_URL` to use HTTPS
   - Configure Nginx for SSL termination

3. **Database**:
   - Use strong passwords
   - Restrict network access
   - Regular backups
   - Consider managed database service

4. **Secrets Management**:
   - Never commit `.env` file
   - Use secrets management service (AWS Secrets Manager, etc.)
   - Rotate credentials regularly

5. **Container Security**:
   - Keep base images updated
   - Use non-root users (already configured)
   - Scan images for vulnerabilities

## 📊 Monitoring

### Health Checks

All services include health checks:

```bash
# Check service status
docker-compose ps

# API health endpoint
curl http://localhost:8000/api/health/

# Frontend health
curl http://localhost:3000/
```

### Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f postgres

# Last 100 lines
docker-compose logs --tail=100 api
```

## 🚨 Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check if postgres is healthy
docker-compose ps postgres

# Restart postgres
docker-compose restart postgres
```

**Port already in use:**
```bash
# Change ports in .env file
API_PORT=8001
FRONTEND_PORT=3001
```

**Permission errors:**
```bash
# Fix volume permissions
docker-compose down
sudo chown -R $USER:$USER .
docker-compose up -d
```

**Frontend can't reach API:**
- Ensure `NEXT_PUBLIC_API_URL` is correctly set
- Check CORS settings in backend
- Verify network connectivity between containers

## 📖 Additional Documentation

- [API Reference](docs/api.md)
- [Architecture Details](docs/architecture.md)
- [Deployment Guide](README.md#production-deployment)
- [Contributing Guidelines](docs/contributing.md)

## 📄 License

[Your License Here]

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Ready to deploy?** Follow the Quick Start guide above and you'll be running in minutes!

