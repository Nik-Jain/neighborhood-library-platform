# Neighborhood Library Platform - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [API Documentation](#api-documentation)
5. [Database Schema](#database-schema)
6. [Deployment Guide](#deployment-guide)
7. [Troubleshooting](#troubleshooting)

## Overview

### Features

✨ **Core Features:**
- 📚 Book Management (Create, Read, Update, Delete)
- 👥 Member Management (Create, Read, Update, Delete)
- 🔄 Borrowing/Returning Operations
- 📊 Tracking and Reporting
- 💰 Fine Management for Overdue Books
- 🔐 Authentication & Authorization
- 📱 Responsive Web Interface

✅ **Quality Metrics:**
- Comprehensive API Documentation (Swagger/OpenAPI)
- Database Normalization with PostgreSQL
- RESTful API Design
- Clean, Maintainable Code
- Unit & Integration Tests
- Docker Support for Easy Deployment

### Tech Stack

**Backend:**
- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15
- Gunicorn

**Frontend:**
- Next.js 14
- React 18
- TailwindCSS
- React Query
- Zustand

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Production)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15 (or Docker)
- Docker & Docker Compose (optional but recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd neighborhood-library-platform

# Copy environment file
cp .env.example .env

# Build and start services
docker-compose up -d

# Run migrations
docker-compose exec api python manage.py migrate

# Create superuser
docker-compose exec api python manage.py createsuperuser

# Seed database with sample data
docker-compose exec api python manage.py seed_database

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
```

### Option 2: Local Development

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Copy environment file
cp ../.env.example ../.env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Seed database
python manage.py seed_database

# Run development server
python manage.py runserver
```

#### Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:3000
```

## Architecture

### Project Structure

```
neighborhood-library-platform/
├── backend/
│   ├── library_service/
│   │   ├── config/              # Django settings & URL configuration
│   │   ├── apps/
│   │   │   └── core/            # Main application
│   │   │       ├── models.py    # Database models (Member, Book, Borrowing, Fine)
│   │   │       ├── views.py     # API viewsets
│   │   │       ├── serializers.py # DRF serializers
│   │   │       ├── filters.py   # Query filters
│   │   │       ├── urls.py      # URL routing
│   │   │       ├── admin.py     # Django admin configuration
│   │   │       ├── exceptions.py # Custom exception handlers
│   │   │       ├── pagination.py # Pagination classes
│   │   │       └── management/  # Custom commands
│   │   └── __init__.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # Reusable components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Utility functions & API client
│   │   └── store/               # State management (Zustand)
│   ├── package.json
│   ├── next.config.js
│   └── Dockerfile
├── scripts/
│   ├── setup.sh                 # Setup script
│   ├── seed_db.sh               # Database seeding
│   └── init_db.sql              # Database initialization
├── docs/                        # Documentation
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### Design Patterns

1. **MVC Pattern**: Django models, views, and templates (DRF for API)
2. **Repository Pattern**: Data access abstraction through ORM
3. **Factory Pattern**: Using factory_boy for test data
4. **Singleton Pattern**: Database connections
5. **Observer Pattern**: Django signals for model updates
6. **Decorator Pattern**: Permission classes, pagination
7. **Strategy Pattern**: Filtering and ordering strategies

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints require token authentication:
```
Authorization: Token <your-token>
```

### Core Endpoints

#### Members Management
- `GET /members/` - List all members with pagination
- `POST /members/` - Create a new member
- `GET /members/{id}/` - Get member details
- `PATCH /members/{id}/` - Update member information
- `DELETE /members/{id}/` - Delete member
- `GET /members/{id}/borrowing_history/` - Get member's borrowing history
- `GET /members/{id}/active_borrowings/` - Get currently active borrowings
- `GET /members/{id}/overdue_borrowings/` - Get overdue borrowings
- `POST /members/{id}/suspend/` - Suspend member account
- `POST /members/{id}/activate/` - Activate member account

#### Books Management
- `GET /books/` - List all books with filtering
- `POST /books/` - Add a new book to library
- `GET /books/{id}/` - Get book details
- `PATCH /books/{id}/` - Update book information
- `DELETE /books/{id}/` - Delete book
- `GET /books/{id}/borrowing_history/` - Get borrowing history
- `POST /books/{id}/increase_copies/` - Increase available copies
- `GET /books/{id}/available_count/` - Check availability

#### Borrowing Operations
- `GET /borrowings/` - List all borrowing transactions
- `POST /borrowings/` - Record a new borrowing
- `GET /borrowings/{id}/` - Get borrowing details
- `POST /borrowings/{id}/return_book/` - Record book return and handle fines
- `GET /borrowings/active/` - Get all active borrowings
- `GET /borrowings/overdue/` - Get overdue borrowings with fines calculation

#### Fine Management
- `GET /fines/` - List all fines
- `GET /fines/{id}/` - Get fine details
- `POST /fines/{id}/mark_as_paid/` - Mark fine as paid
- `GET /fines/unpaid/` - Get unpaid fines only

### Example API Requests

#### Create a Member
```bash
curl -X POST http://localhost:8000/api/v1/members/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "address": "123 Main St",
    "membership_number": "MEM001"
  }'
```

#### Create a Book
```bash
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "isbn": "978-0-133-59266-9",
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "publisher": "Prentice Hall",
    "publication_year": 2008,
    "total_copies": 3,
    "available_copies": 2,
    "condition": "excellent",
    "language": "English"
  }'
```

#### Record a Borrowing
```bash
curl -X POST http://localhost:8000/api/v1/borrowings/ \
  -H "Authorization: Token <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "member_id": "<uuid>",
    "book_id": "<uuid>",
    "notes": "In good condition"
  }'
```

#### Return a Book
```bash
curl -X POST http://localhost:8000/api/v1/borrowings/<borrowing-id>/return_book/ \
  -H "Authorization: Token <token>"
```

## Database Schema

### Entity Relationships

```
Members (1) ----< (Many) Borrowings
Books (1) ----< (Many) Borrowings
Borrowings (1) ----< (0-1) Fines
```

### Detailed Schema

**Members Table**
```
- id (UUID, Primary Key)
- first_name (String, max 100)
- last_name (String, max 100)
- email (Email, Unique)
- phone (String, max 20, Optional)
- address (Text, Optional)
- membership_number (String, max 50, Unique)
- membership_status (ENUM: active, suspended, inactive)
- join_date (Date, auto-set)
- created_at (DateTime, auto-set)
- updated_at (DateTime, auto-update)

Indexes: email, membership_status
```

**Books Table**
```
- id (UUID, Primary Key)
- isbn (String, max 20, Optional, Unique)
- title (String, max 255)
- author (String, max 255)
- publisher (String, max 255, Optional)
- publication_year (Integer, 1000-2100, Optional)
- description (Text, Optional)
- total_copies (Integer, min 1, default 1)
- available_copies (Integer, min 0)
- condition (ENUM: excellent, good, fair, poor)
- language (String, default 'English')
- created_at (DateTime, auto-set)
- updated_at (DateTime, auto-update)

Indexes: title, author, isbn
```

**Borrowings Table**
```
- id (UUID, Primary Key)
- member_id (UUID, Foreign Key → Members)
- book_id (UUID, Foreign Key → Books)
- borrowed_at (DateTime, auto-set)
- due_date (Date, default +14 days)
- returned_at (DateTime, Optional)
- notes (Text, Optional)
- created_at (DateTime, auto-set)
- updated_at (DateTime, auto-update)

Indexes: (member, returned_at), (book, returned_at), due_date
```

**Fines Table**
```
- id (UUID, Primary Key)
- borrowing_id (UUID, Foreign Key → Borrowings, Unique)
- amount (Decimal, 10 digits, 2 decimals)
- reason (String, max 255)
- is_paid (Boolean, default False)
- paid_at (DateTime, Optional)
- created_at (DateTime, auto-set)
- updated_at (DateTime, auto-update)
```

## Deployment Guide

### Production Deployment with Docker

#### 1. Environment Preparation
```bash
# Create production environment file
cp .env.example .env.production

# Update values for production
nano .env.production
```

#### 2. Build and Push Images
```bash
# Build images
docker-compose build

# Tag images
docker tag neighborhood-library-platform-api:latest your-registry/library-api:latest
docker tag neighborhood-library-platform-frontend:latest your-registry/library-frontend:latest

# Push to registry
docker push your-registry/library-api:latest
docker push your-registry/library-frontend:latest
```

#### 3. Deploy to Cloud

**AWS ECS Deployment:**
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/library-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/library-frontend:latest
```

**Heroku Deployment:**
```bash
heroku login
heroku create library-app
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### 4. Security Checklist
- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY` to a secure random value
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure database backups
- [ ] Enable CORS for frontend domain only
- [ ] Set up rate limiting
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Enable database replication/failover

## Troubleshooting

### Database Issues

**Connection Error**
```
Error: could not translate host name "postgres" to address
```
Solution: Ensure PostgreSQL container is running
```bash
docker-compose up -d postgres
```

**Migration Failed**
```bash
# Check migrations
python manage.py showmigrations

# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

### Common Problems

**Port Already in Use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

**Static Files Not Loading**
```bash
python manage.py collectstatic --noinput
```

**CORS Errors**
Update `CORS_ALLOWED_ORIGINS` in settings.py or .env file

**Memory Issues**
Increase Docker memory limit in docker-compose.yml

## Testing

### Run Tests
```bash
# All tests
python manage.py test

# Specific app
python manage.py test library_service.apps.core

# With coverage
pytest --cov=library_service --cov-report=html
```

---

**Version:** 1.0.0  
**Last Updated:** January 2026
