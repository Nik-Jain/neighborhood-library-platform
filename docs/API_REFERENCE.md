# API Quick Reference

## Authentication

All API requests require authentication:

```
Authorization: Token <token>
```

Get your token from Django admin or by logging in.

## Base URL

```
http://localhost:8000/api/v1
```

## Response Format

### Success Response
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/v1/members/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400,
  "details": {...}
}
```

## Common Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Deleted successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Server Error` - Server error

## Filtering & Searching

### List Members
```bash
GET /members/?search=john&membership_status=active&page=1&page_size=20
```

### Search Books
```bash
GET /books/?search=django&is_available=true&ordering=-created_at
```

## Pagination

Default page size: 20, Max page size: 100

```bash
GET /members/?page=2&page_size=50
```

## Examples Using Python

```python
import requests

BASE_URL = 'http://localhost:8000/api/v1'
TOKEN = 'your-token-here'

headers = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}

# Create a member
response = requests.post(
    f'{BASE_URL}/members/',
    headers=headers,
    json={
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'membership_number': 'MEM001'
    }
)

print(response.json())

# Get member
response = requests.get(
    f'{BASE_URL}/members/<id>/',
    headers=headers
)

# List members
response = requests.get(
    f'{BASE_URL}/members/?page=1',
    headers=headers
)

# Record borrowing
response = requests.post(
    f'{BASE_URL}/borrowings/',
    headers=headers,
    json={
        'member_id': '<member-uuid>',
        'book_id': '<book-uuid>'
    }
)

# Return book
response = requests.post(
    f'{BASE_URL}/borrowings/<id>/return_book/',
    headers=headers
)
```

## Examples Using JavaScript/Fetch

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';
const TOKEN = 'your-token-here';

const headers = {
  'Authorization': `Token ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Create member
async function createMember(data) {
  const response = await fetch(`${BASE_URL}/members/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data)
  });
  return response.json();
}

// Get members
async function getMembers(page = 1) {
  const response = await fetch(`${BASE_URL}/members/?page=${page}`, { headers });
  return response.json();
}

// Record borrowing
async function recordBorrowing(memberId, bookId) {
  const response = await fetch(`${BASE_URL}/borrowings/`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      member_id: memberId,
      book_id: bookId
    })
  });
  return response.json();
}

// Return book
async function returnBook(borrowingId) {
  const response = await fetch(`${BASE_URL}/borrowings/${borrowingId}/return_book/`, {
    method: 'POST',
    headers
  });
  return response.json();
}
```

## Webhook Integration (Optional)

You can extend the API to support webhooks for events like:
- Book borrowed
- Book returned
- Fine created
- Book availability changed

Contact support for webhook setup documentation.
