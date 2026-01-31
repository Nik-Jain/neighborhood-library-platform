# Complete Project Structure

## Directory Tree

```
neighborhood-library-platform/
│
├── 📂 backend/                              # Django Backend Application
│   ├── 📂 library_service/                  # Main Django Project
│   │   ├── 📂 config/                       # Django Configuration
│   │   │   ├── __init__.py
│   │   │   ├── settings.py                  # Django settings (DB, apps, middleware)
│   │   │   ├── urls.py                      # URL routing
│   │   │   └── wsgi.py                      # WSGI application
│   │   │
│   │   ├── 📂 apps/                         # Django Applications
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   └── 📂 core/                     # Core Application
│   │   │       ├── 📂 migrations/           # Database migrations
│   │   │       │   └── __init__.py
│   │   │       │
│   │   │       ├── 📂 management/           # Custom Django commands
│   │   │       │   ├── __init__.py
│   │   │       │   └── 📂 commands/
│   │   │       │       ├── __init__.py
│   │   │       │       └── seed_database.py # Populate DB with sample data
│   │   │       │
│   │   │       ├── __init__.py
│   │   │       ├── admin.py                 # Django admin configuration
│   │   │       ├── apps.py                  # App configuration
│   │   │       ├── models.py                # Database models
│   │   │       │   - Member
│   │   │       │   - Book
│   │   │       │   - Borrowing
│   │   │       │   - Fine
│   │   │       │   - TimestampedModel (base)
│   │   │       ├── views.py                 # DRF ViewSets & API endpoints
│   │   │       │   - MemberViewSet
│   │   │       │   - BookViewSet
│   │   │       │   - BorrowingViewSet
│   │   │       │   - FineViewSet
│   │   │       ├── serializers.py           # DRF Serializers (validation)
│   │   │       │   - MemberSerializer
│   │   │       │   - BookSerializer
│   │   │       │   - BorrowingListSerializer
│   │   │       │   - BorrowingDetailSerializer
│   │   │       │   - FineSerializer
│   │   │       ├── filters.py               # Query filters
│   │   │       │   - MemberFilterSet
│   │   │       │   - BookFilterSet
│   │   │       │   - BorrowingFilterSet
│   │   │       ├── pagination.py            # Pagination configuration
│   │   │       │   - StandardResultsSetPagination
│   │   │       ├── exceptions.py            # Custom exception handlers
│   │   │       │   - custom_exception_handler
│   │   │       ├── urls.py                  # App URL routing
│   │   │       └── tests.py                 # Unit & integration tests
│   │   │
│   │   └── __init__.py
│   │
│   ├── manage.py                            # Django management script
│   └── requirements.txt                     # Python dependencies (at root)
│
├── 📂 frontend/                             # Next.js Frontend Application
│   ├── 📂 src/
│   │   ├── 📂 app/                          # Next.js pages (App Router)
│   │   │   ├── layout.tsx                   # Root layout component
│   │   │   ├── page.tsx                     # Dashboard home page
│   │   │   │
│   │   │   ├── 📂 members/
│   │   │   │   └── page.tsx                 # Members list & management
│   │   │   │
│   │   │   ├── 📂 books/
│   │   │   │   └── page.tsx                 # Books catalog page
│   │   │   │
│   │   │   ├── 📂 borrowings/
│   │   │   │   └── page.tsx                 # Borrowings tracking page
│   │   │   │
│   │   │   └── 📂 fines/
│   │   │       └── page.tsx                 # Fines management page
│   │   │
│   │   ├── 📂 components/                   # Reusable React components
│   │   │   └── navigation.tsx               # Navigation bar component
│   │   │
│   │   ├── 📂 hooks/                        # Custom React hooks (React Query)
│   │   │   ├── use-members.ts               # Member CRUD hooks
│   │   │   ├── use-books.ts                 # Book CRUD hooks
│   │   │   ├── use-borrowings.ts            # Borrowing hooks
│   │   │   └── use-fines.ts                 # Fine hooks
│   │   │
│   │   ├── 📂 lib/                          # Utility functions & API client
│   │   │   ├── api-client.ts                # Axios instance with interceptors
│   │   │   └── api.ts                       # API endpoints & types
│   │   │
│   │   └── 📂 store/                        # Zustand state management
│   │       └── auth.ts                      # Authentication store
│   │
│   ├── package.json                         # npm dependencies & scripts
│   ├── next.config.js                       # Next.js configuration
│   ├── tailwind.config.ts                   # TailwindCSS configuration
│   ├── .eslintrc.js                         # ESLint configuration
│   ├── tsconfig.json                        # TypeScript configuration
│   └── Dockerfile                           # Docker image for frontend
│
├── 📂 scripts/                              # Utility scripts
│   ├── setup.sh                             # Development environment setup
│   ├── seed_db.sh                           # Database seeding script
│   └── init_db.sql                          # PostgreSQL initialization
│
├── 📂 docs/                                 # Documentation
│   ├── DEPLOYMENT_GUIDE.md                  # Production deployment guide
│   ├── API_REFERENCE.md                     # API endpoints reference
│   ├── ARCHITECTURE.md                      # Design patterns & architecture
│   └── CONTRIBUTING.md                      # Contributing guidelines
│
├── 📄 docker-compose.yml                    # Multi-container orchestration
│   - PostgreSQL service
│   - Django API service
│   - Next.js Frontend service
│   - Nginx reverse proxy
│
├── 📄 Dockerfile                            # Django application image
├── 📄 .env.example                          # Environment variables template
├── 📄 .gitignore                            # Git ignore patterns
├── 📄 start.sh                              # One-command setup script
├── 📄 requirements.txt                      # Python dependencies
│
├── 📄 README.md                             # Project overview
├── 📄 QUICKSTART.md                         # Quick start guide
├── 📄 IMPLEMENTATION_SUMMARY.md              # Implementation details
└── 📄 PROJECT_COMPLETION.md                 # Feature checklist
```

## Key Files Explained

### Backend Core Files

**models.py** (~200 lines)
- `TimestampedModel`: Abstract base class with auto timestamps
- `Member`: Library member with status tracking
- `Book`: Book inventory with availability
- `Borrowing`: Lending transactions
- `Fine`: Overdue fine records

**views.py** (~250 lines)
- `MemberViewSet`: CRUD + custom actions (suspend, activate)
- `BookViewSet`: CRUD + copy management
- `BorrowingViewSet`: Borrowing operations + return logic
- `FineViewSet`: Fine viewing & payment

**serializers.py** (~200 lines)
- Validation at serializer level
- Nested serializers for relationships
- Custom validation methods

**filters.py** (~50 lines)
- Date range filtering
- Status filtering
- Availability filtering

**urls.py** (~20 lines)
- SimpleRouter for automatic CRUD routes
- Custom action routing

### Frontend Key Files

**layout.tsx** (~30 lines)
- Root layout with QueryClientProvider
- Navigation component
- Main layout structure

**page.tsx** (Dashboard)
- Statistics cards
- Quick action links
- Recent activity

**[resource]/page.tsx** (Member, Book, Borrowing, Fine pages)
- Data listing with tables
- Search & filtering
- Pagination
- CRUD operations

**use-[resource].ts** (Custom Hooks)
- useQuery for data fetching
- useMutation for data modification
- Automatic cache invalidation

**api.ts** (~150 lines)
- TypeScript type definitions
- API endpoint methods
- Request/response handling

## Database Tables

### Members Table
```sql
- id (UUID, PK)
- first_name, last_name
- email (Unique)
- phone, address
- membership_number (Unique)
- membership_status (active|suspended|inactive)
- join_date
- created_at, updated_at
```

### Books Table
```sql
- id (UUID, PK)
- isbn, title, author
- publisher, publication_year
- description
- total_copies, available_copies
- condition (excellent|good|fair|poor)
- language
- created_at, updated_at
```

### Borrowings Table
```sql
- id (UUID, PK)
- member_id (FK)
- book_id (FK)
- borrowed_at
- due_date
- returned_at (nullable)
- notes
- created_at, updated_at
```

### Fines Table
```sql
- id (UUID, PK)
- borrowing_id (FK, Unique)
- amount (Decimal)
- reason
- is_paid
- paid_at (nullable)
- created_at, updated_at
```

## API Routes

```
/api/v1/
├── members/
│   ├── (GET, POST)                    - List, Create
│   ├── {id}/ (GET, PATCH, DELETE)    - Retrieve, Update, Delete
│   ├── {id}/borrowing_history/        - Get history
│   ├── {id}/active_borrowings/        - Get active
│   ├── {id}/overdue_borrowings/       - Get overdue
│   ├── {id}/suspend/                  - Suspend account
│   └── {id}/activate/                 - Activate account
│
├── books/
│   ├── (GET, POST)
│   ├── {id}/ (GET, PATCH, DELETE)
│   ├── {id}/borrowing_history/
│   ├── {id}/increase_copies/
│   └── {id}/available_count/
│
├── borrowings/
│   ├── (GET, POST)
│   ├── {id}/ (GET)
│   ├── {id}/return_book/
│   ├── active/                        - Get active borrowings
│   └── overdue/                       - Get overdue borrowings
│
└── fines/
    ├── (GET)
    ├── {id}/ (GET)
    ├── {id}/mark_as_paid/
    └── unpaid/                        - Get unpaid fines
```

## Frontend Routes

```
/
├── / (dashboard)
├── /members (list)
├── /members/new (create)
├── /members/{id} (detail)
├── /members/{id}/edit (edit)
├── /books (list)
├── /books/new (create)
├── /books/{id} (detail)
├── /books/{id}/edit (edit)
├── /borrowings (list)
├── /borrowings/new (create)
├── /borrowings/{id} (detail)
├── /borrowings/{id}/return (return)
└── /fines (list)
```

## Environment Variables (.env)

```
# Django
DEBUG=False
SECRET_KEY=<secure-random-key>
ALLOWED_HOSTS=yourdomain.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=neighborhood_library
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_HOST=postgres
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://yourdomain.com

# Logging
DJANGO_LOG_LEVEL=INFO

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Docker Services

**postgres**
- PostgreSQL 15 Alpine
- Volume: postgres_data
- Port: 5432

**api**
- Django + Gunicorn
- Builds from Dockerfile
- Port: 8000
- Depends on: postgres

**frontend**
- Next.js Node server
- Builds from frontend/Dockerfile
- Port: 3000
- Depends on: api

**nginx**
- Reverse proxy (production only)
- Port: 80
- Depends on: api, frontend

## Development Tools

**Backend Testing**
- pytest with coverage
- Factory Boy for fixtures
- Mock for mocking

**Frontend Testing**
- Jest for unit tests
- React Testing Library
- Mock server responses

**Code Quality**
- Black (formatting)
- isort (import sorting)
- Flake8 (linting)
- mypy (type checking)
- ESLint (JavaScript)
- Prettier (formatting)

## Configuration Files

**django/config/settings.py** (~200 lines)
- INSTALLED_APPS
- MIDDLEWARE
- DATABASES
- REST_FRAMEWORK settings
- CORS settings
- LOGGING configuration

**next.config.js** (~10 lines)
- React strict mode
- Environment variables
- Build optimization

**docker-compose.yml** (~120 lines)
- 4 services definition
- Volume management
- Environment variables
- Health checks
- Dependencies

**Dockerfile** (~30 lines)
- Python 3.11 base image
- Dependency installation
- Static file collection
- Gunicorn startup

## Lines of Code Summary

| Component | Lines | Purpose |
|-----------|-------|---------|
| Backend Models | 250 | Data structure |
| Backend Views | 300 | API endpoints |
| Backend Serializers | 200 | Validation |
| Backend Tests | 150 | Testing |
| Backend Config | 250 | Settings |
| **Backend Total** | **~1,150** | |
| | | |
| Frontend Pages | 300 | UI pages |
| Frontend Components | 100 | Reusable UI |
| Frontend Hooks | 150 | Data fetching |
| Frontend API | 150 | API client |
| Frontend Store | 50 | State management |
| **Frontend Total** | **~750** | |
| | | |
| Documentation | 3000+ | Guides |
| Configuration | 400 | Docker, env, etc |
| Tests | 150 | Test suite |
| **Grand Total** | **~5,450** | |

---

This complete structure provides a production-ready, scalable, and maintainable library management system.
