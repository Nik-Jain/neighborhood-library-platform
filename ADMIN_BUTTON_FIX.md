# Admin/Librarian UI Fix - Wrong Endpoint Issue

## Problem
Admin and Librarian users were not seeing action buttons to:
- Add members
- Add books
- Record/issue borrowing
- Return books

## Root Cause
Frontend login was calling the **wrong API endpoint** to fetch user groups.

### What Was Happening
```typescript
// WRONG - This endpoint doesn't exist
const userResponse = await apiClient.get('/auth/me/', {...})
// This would fail, and groups would be undefined
```

### Why It Failed
1. Frontend called `/auth/me/` (incorrect endpoint)
2. Endpoint doesn't exist on backend
3. Request failed and was caught in try-catch
4. Fallback stored user data **without groups**
5. `user.groups` was `undefined` or empty
6. `isAdminOrLibrarian()` always returned `false`
7. All admin/librarian buttons hidden

## Solution
Changed frontend to call the **correct endpoint**: `/auth/user/`

```typescript
// CORRECT - Backend endpoint that returns user with groups
const userResponse = await apiClient.get('/auth/user/', {
  headers: { Authorization: `Token ${token}` }
})

// Response includes groups array:
// {
//   "user": {
//     "username": "admin@library.com",
//     "email": "admin@library.com",
//     "groups": ["ADMIN"]  // <-- This is now captured
//   },
//   "member": {...}
// }
```

## Files Changed
- `frontend/src/app/login/page.tsx` - Updated endpoint URL

## Backend Endpoint Reference
The backend has the following auth endpoints:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `POST /api/v1/auth/login/` | Login | Returns `token` + `member` data |
| `GET /api/v1/auth/user/` | Get current user with groups | Returns `user` with `groups` array + `member` data |
| `POST /api/v1/auth/logout/` | Logout | Deletes token |
| `POST /api/v1/auth/signup/` | Register | Creates new member |

## How It Works Now

### Login Flow
```
1. User enters email/password
   ↓
2. POST /api/v1/auth/login/
   ← returns: { token, member }
   ↓
3. GET /api/v1/auth/user/ (with Token header)
   ← returns: { user: {groups: [...]}, member: {...} }
   ↓
4. Store user with groups in auth state
   ↓
5. isAdminOrLibrarian() now returns true
   ↓
6. Admin/Librarian buttons display correctly
```

### Role Detection
```typescript
// Auth store methods now work correctly:
isAdmin()              // checks for 'ADMIN' in groups
isLibrarian()          // checks for 'LIBRARIAN' in groups
isAdminOrLibrarian()   // checks for either 'ADMIN' or 'LIBRARIAN'
isMember()             // checks for 'MEMBER' in groups
```

### UI Rendering
```typescript
// Dashboard and other pages now correctly show/hide buttons
const { isAdminOrLibrarian } = useAuthStore()

{isAdminOrLibrarian() && (
  <Link href="/members/new">Add Member</Link>  // NOW VISIBLE
)}
```

## Testing
To verify the fix works:

1. Start the frontend: `npm run dev` (port 3000)
2. Start the backend: `python manage.py runserver` (port 8000)
3. Login as admin:
   - Email: `admin@library.com`
   - Password: `admin123`
4. Go to dashboard → Should see "Add Member", "Add Book", "Record Borrowing" buttons
5. Go to members page → Should see "Add Member" button
6. Go to books page → Should see "Add Book" button
7. Go to borrowings page → Should see "Record Borrowing" button

## API Endpoints Used

### In Login Flow
```
POST /api/v1/auth/login/
- Input: { email, password }
- Output: { token, member }

GET /api/v1/auth/user/
- Requires: Authorization: Token {token}
- Output: { user: {username, email, groups[]}, member, authenticated }
```

### Response Structure
```json
{
  "user": {
    "username": "admin@library.com",
    "email": "admin@library.com",
    "groups": ["ADMIN"]
  },
  "member": {
    "id": "...",
    "full_name": "Admin User",
    "email": "admin@library.com",
    ...
  },
  "authenticated": true
}
```

## Summary
- **Issue:** Wrong endpoint called → groups not fetched → UI hidden
- **Fix:** Use correct endpoint `/auth/user/` → groups fetched → UI shows correctly
- **Files Modified:** 1 (login/page.tsx)
- **Lines Changed:** 2 (endpoint URL)
- **Impact:** All admin/librarian features now accessible
