# API Reference

Base URL (local): http://localhost:8000/api/v1

## Authentication

Token authentication is required for all endpoints unless DEBUG=True in development.

### Signup

- POST /auth/signup/

Request body:

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "StrongPassword123",
  "password_confirm": "StrongPassword123",
  "phone": "",
  "address": ""
}
```

### Login

- POST /auth/login/

Request body:

```json
{
  "email": "jane@example.com",
  "password": "StrongPassword123"
}
```

### Logout

- POST /auth/logout/

### Current User

- GET /auth/user/

### Legacy Token Endpoint

- POST /api-token-auth/

Same payload as login (email + password).

### Authorization Header

```
Authorization: Token <token>
```

## API Docs and Health

- GET /api/health/
- GET /api/schema/
- GET /api/docs/

## Pagination

List endpoints are paginated.

Query parameters:

- page
- page_size (max 100)

## Members

Base: /members/

- GET /members/
- POST /members/
- GET /members/{id}/
- PATCH /members/{id}/
- DELETE /members/{id}/

Custom actions:

- GET /members/{id}/borrowing_history/
- GET /members/{id}/active_borrowings/
- GET /members/{id}/overdue_borrowings/
- POST /members/{id}/suspend/
- POST /members/{id}/activate/
- POST /members/{id}/change_password/
- GET /members/me/

Filtering, search, ordering:

- Filters: membership_status, join_date_from, join_date_to
- Search: first_name, last_name, email, membership_number
- Ordering: first_name, last_name, join_date, created_at

## Books

Base: /books/

- GET /books/
- POST /books/
- GET /books/{id}/
- PATCH /books/{id}/
- DELETE /books/{id}/

Custom actions:

- GET /books/{id}/borrowing_history/
- POST /books/{id}/increase_copies/
- GET /books/{id}/available_count/

Filtering, search, ordering:

- Filters: condition, language, publication_year_from, publication_year_to, is_available
- Search: title, author, isbn, publisher
- Ordering: title, author, publication_year, created_at

## Borrowings

Base: /borrowings/

- GET /borrowings/
- POST /borrowings/
- GET /borrowings/{id}/
- PATCH /borrowings/{id}/
- DELETE /borrowings/{id}/

Custom actions:

- POST /borrowings/{id}/return_book/
- GET /borrowings/active/
- GET /borrowings/overdue/

Filtering and ordering:

- Filters: member, book, borrowed_from, borrowed_to, due_date_from, due_date_to, is_active
- Ordering: borrowed_at, due_date, created_at

## Fines

Base: /fines/

- GET /fines/
- GET /fines/{id}/

Custom actions:

- POST /fines/{id}/mark_as_paid/
- GET /fines/unpaid/

Filtering:

- Filters: is_paid