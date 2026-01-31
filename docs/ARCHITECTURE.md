# Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Next.js Frontend (React 18, TailwindCSS, Query)  │  │
│  │  - Members Management UI                         │  │
│  │  - Books Catalog UI                              │  │
│  │  - Borrowing Interface                           │  │
│  │  - Fines Dashboard                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│                   API Layer (Nginx Reverse Proxy)       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │      Django REST Framework + Gunicorn            │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │         ViewSets (REST Endpoints)       │    │  │
│  │  │  - MemberViewSet                        │    │  │
│  │  │  - BookViewSet                          │    │  │
│  │  │  - BorrowingViewSet                      │    │  │
│  │  │  - FineViewSet                           │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  │                    ↓                             │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │       Business Logic Layer              │    │  │
│  │  │  - Validations                          │    │  │
│  │  │  - Status Management                    │    │  │
│  │  │  - Fine Calculations                    │    │  │
│  │  │  - Availability Checks                  │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  │                    ↓                             │  │
│  │  ┌─────────────────────────────────────────┐    │  │
│  │  │      ORM Layer (Django Models)          │    │  │
│  │  │  - Member                               │    │  │
│  │  │  - Book                                 │    │  │
│  │  │  - Borrowing                            │    │  │
│  │  │  - Fine                                 │    │  │
│  │  └─────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                            │
│  ┌──────────────────────────────────────────────────┐  │
│  │      PostgreSQL Database                         │  │
│  │  - Members Table                                 │  │
│  │  - Books Table                                   │  │
│  │  - Borrowings Table                              │  │
│  │  - Fines Table                                   │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Design Patterns

### 1. ViewSet Pattern
Used for rapid API development with CRUD operations.

```python
class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    
    @action(detail=True, methods=['get'])
    def active_borrowings(self, request, pk=None):
        # Custom action implementation
        pass
```

### 2. Serializer Hierarchy
Different serializers for different operations.

```python
class MemberListSerializer(serializers.ModelSerializer):
    # Lightweight serializer for list view
    pass

class MemberDetailSerializer(serializers.ModelSerializer):
    # Full serializer for detail view
    pass
```

### 3. Custom Actions
Extended endpoints for specific business operations.

```python
@action(detail=True, methods=['post'])
def return_book(self, request, pk=None):
    # Custom business logic
    pass

@action(detail=False, methods=['get'])
def overdue(self, request):
    # Custom filtering
    pass
```

### 4. Middleware Pattern
For cross-cutting concerns.

```python
# Authentication
class TokenAuthentication

# Pagination
class StandardResultsSetPagination

# Exception Handling
def custom_exception_handler(exc, context):
    pass
```

## Data Flow

### Member Borrowing a Book

```
1. Frontend Request
   POST /api/v1/borrowings/
   {member_id, book_id}
         ↓
2. Serializer Validation
   - Check member exists & is active
   - Check book exists & is available
   - Check member doesn't already have this book
         ↓
3. Business Logic
   - Decrement available_copies
   - Create Borrowing record
   - Set default due_date (+14 days)
         ↓
4. Database Transaction
   - Save to Borrowings table
   - Update Books table
   - Log transaction
         ↓
5. Response
   201 Created with borrowing details
```

### Returning a Book

```
1. Frontend Request
   POST /api/v1/borrowings/{id}/return_book/
         ↓
2. Status Check
   - Verify borrowing exists
   - Check not already returned
         ↓
3. Return Processing
   - Mark returned_at
   - Increment available_copies
   - Check if overdue
         ↓
4. Fine Calculation (if overdue)
   - Calculate days_overdue
   - Calculate fine amount ($0.50/day)
   - Create Fine record
         ↓
5. Database Update
   - Update Borrowing record
   - Update Book availability
   - Create Fine record (if needed)
         ↓
6. Response
   200 OK with updated borrowing details
```

## Frontend Architecture

```
Next.js App Structure:
├── /app                 # Pages (SSR/SSG)
├── /components          # Reusable components
├── /hooks               # Custom React hooks
│   ├── use-members.ts   # Member CRUD operations
│   ├── use-books.ts     # Book CRUD operations
│   ├── use-borrowings.ts # Borrowing operations
│   └── use-fines.ts     # Fine operations
├── /lib
│   ├── api-client.ts    # Axios instance
│   └── api.ts           # API endpoints
└── /store
    └── auth.ts          # Zustand auth store
```

### State Management

```
Zustand Store (Client-side):
└── useAuthStore
    ├── user
    ├── token
    ├── isAuthenticated
    └── methods

React Query (Server-side):
├── Query Cache
├── Mutation Cache
└── Background Sync
```

## Error Handling

### Backend
```python
try:
    # Business logic
except ValidationError as e:
    return Response({'error': str(e)}, status=400)
except ObjectDoesNotExist:
    return Response({'error': 'Not found'}, status=404)
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return Response({'error': 'Server error'}, status=500)
```

### Frontend
```typescript
try {
  await api.create(data);
} catch (error) {
  if (error.response?.status === 400) {
    // Handle validation error
  } else if (error.response?.status === 401) {
    // Redirect to login
  } else {
    // Generic error handling
  }
}
```

## Security Considerations

1. **Authentication**: Token-based (Django REST Framework)
2. **Authorization**: Permission classes on viewsets
3. **Validation**: Serializer-level validation
4. **CSRF**: Enabled by default
5. **SQL Injection**: Protected by ORM
6. **XSS**: Protected by React
7. **Rate Limiting**: Per user/IP
8. **HTTPS**: Required in production
9. **Password Hashing**: PBKDF2 with Django
10. **Environment Variables**: Sensitive data in .env

## Performance Optimization

1. **Database Indexing**
   - Composite indexes on foreign keys
   - Indexes on frequently searched fields

2. **Query Optimization**
   - select_related() for FK relationships
   - prefetch_related() for M2M relationships
   - Pagination (default 20, max 100)

3. **Caching**
   - Query result caching
   - HTTP caching headers

4. **Frontend Optimization**
   - Code splitting with Next.js
   - Image optimization
   - CSS-in-JS with TailwindCSS
   - React Query caching

## Scalability

### Horizontal Scaling
- Multiple API instances behind load balancer
- PostgreSQL replication
- Frontend CDN

### Vertical Scaling
- Gunicorn worker processes
- Database query optimization
- Connection pooling

### Monitoring
- Application logging
- Database query logging
- Error tracking (Sentry, etc.)
- Performance monitoring (APM)

---

For implementation details, see the source code comments and docstrings.
