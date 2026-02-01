# RBAC Quick Reference

## Roles
- **ADMIN**: Full system access, can assign roles
- **LIBRARIAN**: Manage books, members, borrowings, fines
- **MEMBER**: View books, see own borrowings

## Permission Classes

```python
from library_service.apps.core.permissions import (
    IsAdmin,
    IsLibrarian,
    IsAdminOrLibrarian,
    IsMember
)
```

### Usage in Views
```python
class MyViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAdminOrLibrarian()]
        return [IsAuthenticated()]
```

## API Endpoints

### Authentication
```bash
# Signup (creates user with MEMBER role)
POST /api/v1/auth/signup/
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123"
}

# Login
POST /api/v1/auth/login/
{
  "email": "john@example.com",
  "password": "SecurePass123"
}

# Get current user
GET /api/v1/auth/me/
Authorization: Token <your-token>

# Logout
POST /api/v1/auth/logout/
Authorization: Token <your-token>
```

### Books
```bash
# List books (any authenticated user)
GET /api/v1/books/
Authorization: Token <your-token>

# Create book (ADMIN or LIBRARIAN only)
POST /api/v1/books/
Authorization: Token <admin-or-librarian-token>
{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "total_copies": 5,
  "available_copies": 5
}

# Update book (ADMIN or LIBRARIAN only)
PATCH /api/v1/books/{id}/
Authorization: Token <admin-or-librarian-token>
{"available_copies": 3}
```

### Members
```bash
# List members (any authenticated user)
GET /api/v1/members/
Authorization: Token <your-token>

# Create member (ADMIN or LIBRARIAN only)
POST /api/v1/members/
Authorization: Token <admin-or-librarian-token>
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "membership_number": "MEM-123",
  "membership_status": "active"
}

# Suspend member (ADMIN or LIBRARIAN only)
POST /api/v1/members/{id}/suspend/
Authorization: Token <admin-or-librarian-token>
```

### Borrowings
```bash
# List borrowings
# - ADMIN/LIBRARIAN see all
# - MEMBER sees only their own
GET /api/v1/borrowings/
Authorization: Token <your-token>

# Create borrowing (ADMIN or LIBRARIAN only)
POST /api/v1/borrowings/
Authorization: Token <admin-or-librarian-token>
{
  "member": "member-uuid",
  "book": "book-uuid"
}

# Return book (ADMIN or LIBRARIAN only)
POST /api/v1/borrowings/{id}/return_book/
Authorization: Token <admin-or-librarian-token>
```

### Fines
```bash
# List fines (any authenticated user)
GET /api/v1/fines/
Authorization: Token <your-token>

# Mark fine as paid (ADMIN or LIBRARIAN only)
POST /api/v1/fines/{id}/mark_as_paid/
Authorization: Token <admin-or-librarian-token>
```

## Management Commands

```bash
# Bootstrap roles and create admin
python manage.py bootstrap_roles --username admin --email admin@library.local --password admin123

# Seed sample data
python manage.py seed_database

# Run RBAC tests
python manage.py test library_service.apps.core.tests_permissions
python manage.py test library_service.apps.core.tests_rbac_integration
```

## Assigning Roles (Python Shell)

```python
from django.contrib.auth.models import User, Group

# Get user
user = User.objects.get(username='user@example.com')

# Assign LIBRARIAN role
librarian_group = Group.objects.get(name='LIBRARIAN')
user.groups.add(librarian_group)

# Remove MEMBER role
member_group = Group.objects.get(name='MEMBER')
user.groups.remove(member_group)

# Check user's roles
user.groups.values_list('name', flat=True)
# Output: ['LIBRARIAN']
```

## Common Scenarios

### Promote Member to Librarian
```python
user = User.objects.get(username='member@library.local')
member_group = Group.objects.get(name='MEMBER')
librarian_group = Group.objects.get(name='LIBRARIAN')
user.groups.remove(member_group)
user.groups.add(librarian_group)
```

### Create Admin User Manually
```python
from django.contrib.auth.models import User, Group

user = User.objects.create_user(
    username='newadmin@library.local',
    email='newadmin@library.local',
    password='SecurePass123'
)
admin_group = Group.objects.get(name='ADMIN')
user.groups.add(admin_group)
```

### Check Permissions in View
```python
# In a view or viewset method
def my_action(self, request):
    user = request.user
    
    # Check if user is admin
    is_admin = user.groups.filter(name='ADMIN').exists()
    
    # Check if user is admin or librarian
    is_staff = user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists()
    
    if not is_staff:
        return Response({'error': 'Permission denied'}, status=403)
    
    # ... continue with action
```

## Testing

### Test as Different Roles
```bash
# 1. Login as admin
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@library.local", "password": "admin123"}'

# Save token from response
ADMIN_TOKEN="<token-from-response>"

# 2. Create a book (should succeed)
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Authorization: Token $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book", "author": "Author", "total_copies": 1, "available_copies": 1}'

# 3. Login as member
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "member@library.local", "password": "password123"}'

MEMBER_TOKEN="<token-from-response>"

# 4. Try to create a book (should fail with 403)
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Authorization: Token $MEMBER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Book 2", "author": "Author", "total_copies": 1, "available_copies": 1}'
```

## Troubleshooting

### Token doesn't work after implementation
**Solution**: Users need to re-login to get new APIToken

### Permission denied even with correct role
**Solution**: Check that:
1. User is authenticated: `request.user.is_authenticated`
2. User has correct group: `request.user.groups.filter(name='ADMIN').exists()`
3. Token is valid and not expired

### Member created but can't login
**Solution**: Check that:
1. `membership_status` is 'active'
2. Signal created Django User (check `User.objects.filter(username=member.email)`)
3. User has MEMBER group assigned

### Migrations fail
**Solution**: 
```bash
# Delete migration files (except __init__.py)
rm backend/library_service/apps/core/migrations/0*.py

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```
