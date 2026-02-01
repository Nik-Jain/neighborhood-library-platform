# Frontend RBAC Implementation

## Overview
Updated the frontend to properly integrate with the backend RBAC system, ensuring that members only see content and actions appropriate to their role.

## Changes Made

### 1. Auth Store Updates (`frontend/src/store/auth.ts`)

**Added:**
- `groups?: string[]` field to User interface
- Helper methods:
  - `isAdmin()` - Checks if user has ADMIN role
  - `isLibrarian()` - Checks if user has LIBRARIAN role  
  - `isAdminOrLibrarian()` - Checks if user has ADMIN or LIBRARIAN role
  - `isMember()` - Checks if user has MEMBER role

**Purpose:** 
- Store user's group memberships from the backend
- Provide convenient role-checking methods for UI components

### 2. Login Flow Updates (`frontend/src/app/login/page.tsx`)

**Added:**
- After successful login, fetch user data from `/auth/me/` endpoint
- Extract user groups from the response
- Store full user object with groups in auth store

**Purpose:**
- Ensure user groups are loaded and available for role-based UI rendering
- Fallback to basic user data if `/auth/me/` fails

### 3. Dashboard Updates (`frontend/src/app/page.tsx`)

**Added:**
- Role-based Quick Actions section
- For ADMIN/LIBRARIAN: Show "Add New Member", "Add New Book", "Record Borrowing"
- For MEMBER: Show "Browse Books", "My Borrowings"

**Purpose:**
- Hide administrative actions from regular members
- Provide relevant quick actions based on user role

### 4. Borrowings Page Updates (`frontend/src/app/borrowings/page.tsx`)

**Added:**
- Conditional page title: "Borrowings" for admin/librarian, "My Borrowings" for members
- Hide "Record Borrowing" button from members
- Import and use `useAuthStore` for role checks

**Purpose:**
- Members can only see their own borrowings (enforced by backend)
- Hide borrowing creation UI from members
- Clear indication to members they're viewing their own borrowings

### 5. Members Page Updates (`frontend/src/app/members/page.tsx`)

**Added:**
- Hide "Add Member" button from members
- Hide edit and delete action buttons from members
- Keep "View" button visible to all users

**Purpose:**
- Prevent members from accessing member creation/modification UI
- Members can still view member profiles but cannot modify them

### 6. Books Page Updates (`frontend/src/app/books/page.tsx`)

**Added:**
- Hide "Add Book" button from members
- Hide edit and delete action buttons from members
- Keep "View" button visible to all users

**Purpose:**
- Prevent members from accessing book creation/modification UI
- Members can browse and view book details but cannot modify them

## Role Permissions Summary

### ADMIN Role
- Full access to all features
- Can create, read, update, delete: members, books, borrowings, fines
- Dashboard shows all statistics and admin quick actions

### LIBRARIAN Role
- Same as ADMIN for most operations
- Can manage members, books, borrowings, and fines
- Dashboard shows all statistics and admin quick actions

### MEMBER Role
- **Borrowings:** Can only view their own borrowings (backend filters automatically)
- **Books:** Can view all books but cannot add/edit/delete
- **Members:** Can view member profiles but cannot add/edit/delete
- **Fines:** Can view fines (backend will filter to show only their own)
- **Dashboard:** Shows member-focused quick actions (Browse Books, My Borrowings)
- Cannot access:
  - Member creation/editing
  - Book creation/editing
  - Borrowing creation (recording new borrowings)
  - Fine management

## Backend Integration

The frontend role checks work in conjunction with backend permissions:

1. **Backend `/auth/me/` endpoint** returns:
   ```json
   {
     "user": {
       "id": 1,
       "username": "john_member",
       "email": "john@example.com",
       "groups": ["MEMBER"]
     },
     "member": {
       "id": 1,
       "full_name": "John Doe",
       ...
     }
   }
   ```

2. **Backend enforces permissions at API level:**
   - Returns 403 Forbidden for unauthorized actions
   - Filters queryset for object-level permissions (e.g., members only see own borrowings)

3. **Frontend provides UI-level security:**
   - Hides UI elements for actions users cannot perform
   - Provides better UX by not showing disabled buttons
   - Prevents unnecessary API calls that would return 403

## Testing Recommendations

### Test Member Role Restrictions:
1. Log in as a member
2. Verify dashboard shows "Browse Books" and "My Borrowings" only
3. Navigate to Members page - should not see "Add Member" button
4. Navigate to Books page - should not see "Add Book" button
5. Navigate to Borrowings page - should only see own borrowings, no "Record Borrowing" button
6. Try to access `/members/new`, `/books/new`, `/borrowings/new` directly - should get 403 from backend

### Test Admin/Librarian Roles:
1. Log in as admin or librarian
2. Verify all admin quick actions are visible on dashboard
3. Verify can see "Add Member", "Add Book", "Record Borrowing" buttons
4. Verify can see edit/delete buttons in lists
5. Verify can access all features without restrictions

## Security Notes

1. **Defense in Depth:** Frontend UI restrictions complement backend permission checks but do not replace them
2. **Backend is the Source of Truth:** All security enforcement happens at the API level
3. **UI Restrictions Improve UX:** Hiding unauthorized actions prevents confusion and unnecessary error messages
4. **Direct URL Access:** Users attempting to access unauthorized pages directly will receive 403 errors from the backend

## Future Enhancements

Consider adding:
1. Route guards to prevent navigation to unauthorized pages
2. Error boundary for 403 responses with user-friendly messages
3. Role badge in navigation showing current user's role
4. Loading states while fetching user groups
5. Refresh mechanism to update groups if changed on backend
