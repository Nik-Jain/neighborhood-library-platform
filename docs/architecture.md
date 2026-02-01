# Architecture

This document describes the backend architecture for the Neighborhood Library Platform.

## System Context

```
Clients (Web, Admin, API Clients)
            |
            v
    Django REST API (Gunicorn)
            |
            v
        PostgreSQL
```

Nginx is optional and can be enabled as a reverse proxy in production deployments.

## Backend Components

### Django Project Layout

- library_service/config: settings, URL routing, WSGI
- library_service/apps/core: domain logic (models, serializers, viewsets, permissions)

### Core Domain Models

- Member: library user profile with membership status
- Book: inventory item with availability tracking
- Borrowing: loan transaction with due date and return tracking
- Fine: one-to-one fine generated for overdue borrowings
- APIToken: token model for API authentication

### Request Flow (Example: Borrow a Book)

1. Client posts to /api/v1/borrowings/ with member_id and book_id.
2. Borrowing serializer validates member status and book availability.
3. Viewset creates the borrowing, updates book availability, returns a detailed response.

## Authentication and RBAC

- Token authentication using APIToken.
- Role-based access control via Django groups: ADMIN, LIBRARIAN, MEMBER.
- Permissions are enforced in viewsets and custom actions.

## API Layer

- Django REST Framework viewsets for CRUD operations.
- Custom actions for domain workflows (return_book, mark_as_paid, etc.).
- Filtering, searching, ordering, and pagination built in.

## Configuration and Environments

- Configuration is driven by .env with defaults in .env.example.
- DEBUG toggles permissive access for local development; production should set DEBUG=False.

## Observability

- Health check endpoint: /api/health/
- Structured logging to console and rotating file handler

## Performance Considerations

- Pagination: default page size 20, max 100
- Query optimization via indexes on common filter/search fields