# RBAC Implementation Summary

## Overview
Comprehensive Role-Based Access Control (RBAC) implementation for the neighborhood library platform using Django Groups and DRF permissions.

## Changes Made

### 1. New Files Created

#### Core RBAC Components
- **`permissions.py`**: DRF permission classes
  - `IsAdmin`: Allows only ADMIN users
  - `IsLibrarian`: Allows only LIBRARIAN users  
  - `IsAdminOrLibrarian`: Allows ADMIN or LIBRARIAN users
  - `IsMember`: Allows only MEMBER users

- **`utils.py`**: Role management utilities
  - `assign_default_member_role()`: Assigns MEMBER role to users
  - `ensure_roles_exist()`: Creates all required groups
  - `get_or_create_group()`: Helper to manage groups

- **`signals.py`**: Auto-sync Member → User
  - Creates Django User for each Member (email → username)
  - Assigns MEMBER role automatically
  - Syncs `is_active` based on `membership_status`

- **`token_models.py`**: APIToken model
  - Links tokens to Django Users (enables group-based permissions)
  - Tracks token creation and last use
  - Auto-generates secure 40-char hex tokens

#### Management Commands
- **`bootstrap_roles.py`**: Setup command
  - Creates ADMIN, LIBRARIAN, MEMBER groups
  - Creates superuser with ADMIN role
  - Syncs existing Members to Users

#### Tests
- **`tests_permissions.py`**: Unit tests for permission classes
  - Tests each permission class with different user roles
  - Tests anonymous/unauthenticated access
  - Tests users with no groups

- **`tests_rbac_integration.py`**: Integration tests for API endpoints
  - Tests book create/update/delete (IsAdminOrLibrarian)
  - Tests member create/update (IsAdminOrLibrarian)
  - Tests borrowing operations (IsAdminOrLibrarian)
  - Tests member-only views (object-level filtering)
  - Tests fine management (IsAdminOrLibrarian for mark_as_paid)

### 2. Modified Files

#### Authentication
- **`authentication.py`**: Complete rewrite
  - Replaced `SimpleTokenAuth` with `APITokenAuthentication`
  - Now returns real Django User objects (with `.groups` support)
  - Validates tokens against APIToken table
  - Updates `last_used_at` on each request

- **`auth_views.py`**: Updated to use APIToken
  - `SignupView`: Creates APIToken after Member creation
  - `LoginView`: Returns existing or creates new APIToken
  - `LogoutView`: Deletes user's APITokens
  - `CurrentUserView`: Returns user info including groups

#### Views & Permissions
- **`views.py`**: Applied RBAC permissions to all viewsets
  - `MemberViewSet`: IsAdminOrLibrarian for CUD operations
  - `BookViewSet`: IsAdminOrLibrarian for CUD operations
  - `BorrowingViewSet`: IsAdminOrLibrarian for create/return; MEMBERs see only own borrowings
  - `FineViewSet`: IsAdminOrLibrarian for mark_as_paid

#### Configuration
- **`settings.py`**: Updated authentication class
  - Changed from `SimpleTokenAuth` to `APITokenAuthentication`

- **`apps.py`**: Load signals on app ready
  - Imports signals module to register handlers

- **`models.py`**: Import APIToken
  - Added import at end to make APIToken available

- **`admin.py`**: Register APIToken
  - Added admin interface for viewing tokens

#### Database Seeding
- **`seed_database.py`**: Enhanced to support RBAC
  - Calls `ensure_roles_exist()` before seeding
  - Adds admin user to ADMIN group

### 3. Permission Rules Applied

| Endpoint | Action | Required Role |
|----------|--------|---------------|
| Books - List/Read | GET | Any authenticated user |
| Books - Create/Update/Delete | POST/PUT/PATCH/DELETE | ADMIN or LIBRARIAN |
| Members - List/Read | GET | Any authenticated user |
| Members - Create/Update/Delete | POST/PUT/PATCH/DELETE | ADMIN or LIBRARIAN |
| Members - Suspend/Activate | POST | ADMIN or LIBRARIAN |
| Borrowings - List | GET | All: ADMIN/LIBRARIAN see all; MEMBER sees own only |
| Borrowings - Create | POST | ADMIN or LIBRARIAN |
| Borrowings - Return Book | POST | ADMIN or LIBRARIAN |
| Fines - List/Read | GET | Any authenticated user |
| Fines - Mark as Paid | POST | ADMIN or LIBRARIAN |

### 4. Object-Level Permissions

**BorrowingViewSet** implements filtering in `get_queryset()`:
- ADMIN and LIBRARIAN: See all borrowings
- MEMBER: See only their own borrowings (filtered by linked Member record)

## Setup Instructions

### Using Docker (Recommended)

```bash
# 1. Start Docker containers
docker-compose up -d

# 2. Run RBAC setup script
chmod +x scripts/setup_rbac.sh
docker-compose exec api bash scripts/setup_rbac.sh
```

### Manual Setup

```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Run migrations
python manage.py migrate

# 3. Bootstrap roles and admin
python manage.py bootstrap_roles --username admin --email admin@library.local --password admin123

# 4. (Optional) Seed sample data
python manage.py seed_database

# 5. Run tests
python manage.py test library_service.apps.core.tests_permissions
python manage.py test library_service.apps.core.tests_rbac_integration
```

## Testing the Implementation

### 1. Login as Admin
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@library.local", "password": "admin123"}'
```

Response includes token and user groups:
```json
{
  "token": "abc123...",
  "member": {...},
  "message": "Login successful"
}
```

### 2. Test Protected Endpoint
```bash
# Admin can create books
curl -X POST http://localhost:8000/api/v1/books/ \
  -H "Authorization: Token <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "author": "Author Name", "total_copies": 5, "available_copies": 5}'
```

### 3. Get Current User Info
```bash
curl http://localhost:8000/api/v1/auth/me/ \
  -H "Authorization: Token <your-token>"
```

Returns groups: `["ADMIN"]` for admin user

### 4. Test Member Sees Only Own Borrowings
```bash
# Login as a member
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "member@library.local", "password": "password123"}'

# List borrowings (will only see own)
curl http://localhost:8000/api/v1/borrowings/ \
  -H "Authorization: Token <member-token>"
```

## Backward Compatibility

### Signal-Based Sync
- New Members automatically get Django User accounts (via post_save signal)
- Existing Members are synced when running `bootstrap_roles` command
- No breaking changes to Member model schema

### Token Migration
- Old token format is replaced by APIToken model
- Users need to re-login to get new tokens
- Tokens now properly link to Django Users with groups

### Frontend Changes Required
- Frontend should continue using same auth endpoints
- Token format remains the same (40-char hex)
- `/api/v1/auth/me/` now returns `groups` array

## Running Tests

```bash
# Unit tests for permissions
python manage.py test library_service.apps.core.tests_permissions -v 2

# Integration tests for secured endpoints
python manage.py test library_service.apps.core.tests_rbac_integration -v 2

# Run all tests
python manage.py test library_service.apps.core -v 2
```

## Architecture Notes

### Why Django Users + Member Model?
- Django's Group/Permission system works with `User` model
- Preserves existing `Member` model as primary domain model
- Signal keeps them in sync automatically
- Users have username=member.email for auth

### Token Design
- `APIToken` links to Django `User` (not Member directly)
- Enables `request.user.groups.filter(...)` in permissions
- Tracks usage via `last_used_at`
- Can have multiple tokens per user (logout deletes all)

### Permission Workflow
1. Request comes with `Authorization: Token <key>`
2. `APITokenAuthentication` looks up token → gets User
3. DRF sets `request.user` to the User object
4. Permission classes check `request.user.groups`
5. View can filter queryset based on groups

## Future Enhancements

1. **Token Expiry**: Add `expires_at` field to APIToken
2. **Role Assignment Endpoint**: Add API for admins to assign roles
3. **Audit Logging**: Log role changes and privileged actions
4. **Fine-Grained Permissions**: Django's built-in permissions for specific actions
5. **Token Revocation**: Admin panel to revoke/manage tokens
6. **Multi-Factor Auth**: Add 2FA for admin/librarian accounts
