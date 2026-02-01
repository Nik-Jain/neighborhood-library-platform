# Frontend RBAC Testing Guide

## Prerequisites

Before testing, ensure:
1. Backend server is running
2. Bootstrap roles command has been executed (`python manage.py bootstrap_roles`)
3. At least one user exists for each role (ADMIN, LIBRARIAN, MEMBER)
4. Frontend development server is running

## Test Users

From the bootstrap command, you should have:
- **Admin User:**
  - Email: `admin@library.com`
  - Password: `admin123`
  - Role: ADMIN

You'll need to create test users for other roles or use existing members.

## Testing Scenarios

### 1. Member Role Testing

#### 1.1 Login as Member
1. Navigate to `/login`
2. Login with a member account
3. **Expected:** Successful login, redirected to dashboard

#### 1.2 Dashboard View
**Expected UI Elements:**
- Title: "Dashboard"
- Statistics cards showing total books, members, active borrowings
- Quick Actions section with ONLY:
  - "Browse Books" button
  - "My Borrowings" button
- NO "Add New Member", "Add New Book", or "Record Borrowing" buttons

#### 1.3 Navigation Bar
**Expected:**
- User name displayed
- Email displayed
- Role badge showing "Member" in primary color
- Logout button visible

#### 1.4 Books Page
1. Navigate to `/books`
2. **Expected:**
   - Can view list of all books
   - Search functionality works
   - "View" (eye icon) button visible for each book
   - NO "Add Book" button at top
   - NO "Edit" or "Delete" buttons for any book

#### 1.5 Members Page
1. Navigate to `/members`
2. **Expected:**
   - Can view list of all members
   - Search functionality works
   - "View" (eye icon) button visible for each member
   - NO "Add Member" button at top
   - NO "Edit" or "Delete" buttons for any member

#### 1.6 Borrowings Page
1. Navigate to `/borrowings`
2. **Expected:**
   - Page title: "My Borrowings"
   - Only shows borrowings for the logged-in member
   - Filter tabs work (All/Active/Overdue)
   - NO "Record Borrowing" button at top
   - List shows only borrowings where member is the borrower

#### 1.7 Fines Page
1. Navigate to `/fines`
2. **Expected:**
   - Shows fines (backend should filter to member's own fines)
   - Can toggle between "Show All" and "Show Unpaid Only"
   - No action buttons (read-only view)

#### 1.8 Unauthorized Access Attempts
Try to access these URLs directly:
- `/members/new` - Should show 404 or empty form, API POST will return 403
- `/books/new` - Should show 404 or empty form, API POST will return 403
- `/borrowings/new` - Should show 404 or empty form, API POST will return 403

**Expected:** 
- Frontend may show the page (no route guard yet)
- But submitting any form will return 403 Forbidden from backend
- Or page may not exist/work properly

### 2. Admin/Librarian Role Testing

#### 2.1 Login as Admin
1. Navigate to `/login`
2. Login with admin credentials
3. **Expected:** Successful login, redirected to dashboard

#### 2.2 Dashboard View
**Expected UI Elements:**
- Title: "Dashboard"
- All statistics cards visible
- Quick Actions section with:
  - "Add New Member" button
  - "Add New Book" button
  - "Record Borrowing" button

#### 2.3 Navigation Bar
**Expected:**
- User name displayed
- Email displayed
- Role badge showing "Admin" or "Librarian" in primary color
- Logout button visible

#### 2.4 Books Page
**Expected:**
- "Add Book" button visible at top
- "View", "Edit", and "Delete" buttons visible for each book
- All books visible in list
- Can perform all CRUD operations

#### 2.5 Members Page
**Expected:**
- "Add Member" button visible at top
- "View", "Edit", and "Delete" buttons visible for each member
- All members visible in list
- Can perform all CRUD operations

#### 2.6 Borrowings Page
**Expected:**
- Page title: "Borrowings"
- "Record Borrowing" button visible at top
- Shows ALL borrowings for all members
- Filter tabs work
- Can create new borrowings

#### 2.7 Fines Page
**Expected:**
- Shows all fines for all members
- Can toggle between "Show All" and "Show Unpaid Only"
- May have action buttons if implemented

### 3. Role Switching Test

#### 3.1 Switch from Member to Admin
1. Login as member
2. Verify member UI restrictions
3. Logout
4. Login as admin
5. Verify admin UI shows all features
6. **Expected:** UI updates correctly based on role

#### 3.2 Switch from Admin to Member
1. Login as admin
2. Verify admin UI features
3. Logout
4. Login as member
5. Verify member UI restrictions
6. **Expected:** UI restricts features appropriately

### 4. Backend Permission Enforcement

Even though frontend hides buttons, test backend permissions:

#### 4.1 Member Cannot Create Borrowings
1. Login as member
2. Open browser DevTools
3. Try to POST to `/api/borrowings/`:
   ```javascript
   fetch('http://localhost:8000/api/borrowings/', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': 'Token YOUR_TOKEN_HERE'
     },
     body: JSON.stringify({
       member_id: 1,
       book_id: 1
     })
   })
   ```
4. **Expected:** 403 Forbidden response

#### 4.2 Member Cannot Edit Books
1. Login as member
2. Try to PATCH to `/api/books/1/`:
   ```javascript
   fetch('http://localhost:8000/api/books/1/', {
     method: 'PATCH',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': 'Token YOUR_TOKEN_HERE'
     },
     body: JSON.stringify({
       title: 'Hacked Title'
     })
   })
   ```
3. **Expected:** 403 Forbidden response

#### 4.3 Member Only Sees Own Borrowings
1. Login as member with ID 1
2. Check borrowings response
3. **Expected:** Only borrowings where `member.id === 1`

### 5. UI/UX Quality Checks

#### 5.1 Visual Consistency
- Role badge in navigation is properly styled
- Quick Actions sections are well-aligned
- No broken layouts when buttons are hidden
- Proper spacing and alignment on all pages

#### 5.2 User Experience
- Member sees helpful page titles ("My Borrowings" vs "Borrowings")
- No confusing empty button slots
- Clear indication of user's role in navigation
- Logout works from any page

#### 5.3 Performance
- Page doesn't flicker when loading role-based UI
- Auth state loads quickly from localStorage
- No unnecessary re-renders

## Common Issues and Solutions

### Issue: Role badge not showing
**Solution:** 
- Check if `/auth/me/` is being called after login
- Verify groups are in localStorage under 'user' key
- Check browser console for errors

### Issue: Member sees admin buttons
**Solution:**
- Clear localStorage and login again
- Verify backend is returning correct groups in `/auth/me/`
- Check if user was assigned to MEMBER group

### Issue: Dashboard statistics not loading
**Solution:**
- Check network tab for API errors
- Verify backend endpoints are accessible
- Check CORS configuration if running on different ports

### Issue: 403 errors not handled gracefully
**Solution:**
- This is expected for unauthorized actions
- Future enhancement: Add error boundaries and user-friendly messages

## Test Checklist

### Member Role ✓
- [ ] Dashboard shows member quick actions only
- [ ] Navigation shows "Member" badge
- [ ] Books page: no add/edit/delete buttons
- [ ] Members page: no add/edit/delete buttons
- [ ] Borrowings page: shows "My Borrowings", own borrowings only, no record button
- [ ] Fines page: shows own fines only
- [ ] Direct API calls return 403 for unauthorized actions

### Admin/Librarian Role ✓
- [ ] Dashboard shows all quick actions
- [ ] Navigation shows "Admin" or "Librarian" badge
- [ ] Books page: all buttons visible
- [ ] Members page: all buttons visible
- [ ] Borrowings page: shows "Borrowings", all borrowings, record button visible
- [ ] Fines page: shows all fines
- [ ] Can perform all CRUD operations

### General ✓
- [ ] Login/logout works correctly
- [ ] Role switching updates UI appropriately
- [ ] Auth state persists on page refresh
- [ ] No console errors
- [ ] Visual consistency maintained
- [ ] Backend enforces permissions regardless of UI

## Automated Testing (Future)

Consider adding:
1. **Component tests** for role-based rendering
2. **Integration tests** for login flow with role fetching
3. **E2E tests** for complete user journeys per role
4. **API mocking** to test 403 response handling

## Manual Verification Script

```bash
# 1. Start backend
cd backend
python manage.py runserver

# 2. In another terminal, start frontend
cd frontend
npm run dev

# 3. Access application
# Browser: http://localhost:3000

# 4. Test each role systematically using the checklist above
```

## Reporting Issues

When reporting frontend RBAC issues, include:
1. User role being tested
2. Page/component where issue occurs
3. Expected behavior vs actual behavior
4. Browser console errors (if any)
5. Network tab showing API requests/responses
6. Screenshot of the issue
