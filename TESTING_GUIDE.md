# Step-by-Step Testing Guide for Authentication

## Prerequisites
- Backend server running on http://localhost:8000
- Frontend running on http://localhost:3000
- Database migrations applied

## Test Scenario 1: User Signup and Login

### Step 1: Visit Signup Page
1. Go to http://localhost:3000/signup
2. You should see the signup form with:
   - First name field
   - Last name field
   - Email field
   - Phone field (optional)
   - Address field (optional)
   - Password field
   - Confirm password field

### Step 2: Create New Account
1. Fill in the form:
   - First Name: `Alice`
   - Last Name: `Johnson`
   - Email: `alice.johnson@example.com`
   - Password: `TestPassword123`
   - Confirm Password: `TestPassword123`
2. Click "Create Account"
3. You should see: "Account created successfully! Redirecting..."
4. Page should redirect to dashboard in ~2 seconds

### Step 3: Verify Dashboard Access
1. You should be on the dashboard (/)
2. Navigation bar should show: "Alice Johnson" in top-right
3. Email "alice.johnson@example.com" should be visible under name
4. Dashboard stats should be displayed (Books, Members, Borrowings)

### Step 4: Logout
1. Click "Logout" button in top-right navigation
2. You should be redirected to login page (/login)
3. localStorage should be cleared

---

## Test Scenario 2: Login with Created Account

### Step 1: Visit Login Page
1. Go to http://localhost:3000/login
2. You should see the login form with:
   - Email field
   - Password field
   - "Sign In" button
   - "Create Account" link
   - Demo credentials display

### Step 2: Login with New Account
1. Enter credentials:
   - Email: `alice.johnson@example.com`
   - Password: `TestPassword123`
2. Click "Sign In"
3. You should see: "Signing in..."
4. Page should redirect to dashboard

### Step 3: Verify Dashboard
1. Dashboard should load with your user info in navigation
2. Click "Logout" to test logout

---

## Test Scenario 3: Login with Admin Credentials

### Step 1: Visit Login Page
1. Go to http://localhost:3000/login
2. Demo credentials are displayed at bottom

### Step 2: Login with Admin
1. Use demo credentials shown on page:
   - Email: `admin@library.local`
   - Password: `admin123`
2. Click "Sign In"
3. Should redirect to dashboard with "Admin User" in navigation

---

## Test Scenario 4: Error Handling

### Step 1: Test Invalid Email
1. Go to http://localhost:3000/login
2. Enter:
   - Email: `nonexistent@example.com`
   - Password: `password123`
3. Click "Sign In"
4. You should see error: "Invalid email or password."

### Step 2: Test Wrong Password
1. Go to http://localhost:3000/login
2. Enter:
   - Email: `admin@library.local`
   - Password: `wrongpassword`
3. Click "Sign In"
4. You should see error: "Invalid email or password."

### Step 3: Test Signup Validation
1. Go to http://localhost:3000/signup
2. Try to submit with:
   - Empty first name → Error: "First name is required"
   - Empty email → Error: "Email is required"
   - Password < 8 chars → Error: "Password must be at least 8 characters"
   - Non-matching passwords → Error: "Passwords do not match"
   - Existing email → Error: "An account with this email already exists"

---

## Test Scenario 5: Token Management

### Using curl to test API directly:

#### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob.smith@example.com",
    "password": "BobPassword123",
    "password_confirm": "BobPassword123"
  }'
```

Expected Response:
```json
{
  "token": "a1b2c3d4e5f6...",
  "member": {
    "id": "...",
    "first_name": "Bob",
    "last_name": "Smith",
    "email": "bob.smith@example.com",
    "full_name": "Bob Smith",
    ...
  },
  "message": "Account created successfully"
}
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob.smith@example.com",
    "password": "BobPassword123"
  }'
```

Expected Response: Same as signup response with token and member details

#### Use Token to Access Protected Endpoint
```bash
# Save token from login response
TOKEN="a1b2c3d4e5f6..."

# Access members endpoint with token
curl -X GET http://localhost:8000/api/v1/members/ \
  -H "Authorization: Token $TOKEN"
```

Expected Response: List of members (or empty list if none exist)

#### Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token $TOKEN"
```

Expected Response:
```json
{
  "message": "Logout successful"
}
```

---

## Test Scenario 6: Protected Routes

### Step 1: Logout (if logged in)
1. Go to http://localhost:3000
2. If dashboard loads, click "Logout"
3. Clear browser localStorage manually if needed

### Step 2: Try to Access Protected Route
1. Go to http://localhost:3000/members
2. You should be redirected to http://localhost:3000/login
3. Access to protected pages requires authentication

### Step 3: Login and Access Protected Route
1. Go to http://localhost:3000/login
2. Login with admin credentials
3. Go to http://localhost:3000/members
4. Members page should load

---

## Test Scenario 7: Token Persistence

### Step 1: Login and Verify
1. Go to http://localhost:3000/login
2. Login with any valid credentials
3. Navigate to dashboard
4. Open browser DevTools → Application → LocalStorage
5. You should see:
   - `authToken`: The 40-character token
   - `user`: JSON object with member details

### Step 2: Refresh Page
1. While logged in, refresh the page (Ctrl+R or Cmd+R)
2. Dashboard should still be visible
3. No login should be required
4. Auth state should be restored from localStorage

### Step 3: Close and Reopen Browser
1. Login to the app
2. Close the browser tab/window
3. Reopen http://localhost:3000
4. Dashboard should load without login (if session is fresh)

---

## Test Scenario 8: Navigation Menu

### Step 1: Unauthenticated State
1. Go to http://localhost:3000/login
2. Logout if necessary
3. Navigation should show:
   - Library logo
   - "Sign In" button
   - "Sign Up" button

### Step 2: Authenticated State
1. Login with admin credentials
2. Navigation should show:
   - Library logo
   - Dashboard, Members, Books, Borrowings, Fines links
   - User info (name and email)
   - "Logout" button

### Step 3: Mobile Menu
1. Resize browser to mobile size (< 768px)
2. Click hamburger menu icon
3. Menu should show all links and logout button
4. Click a link → page navigates and menu closes
5. Click "Logout" → logged out and redirected to login

---

## Troubleshooting

### Issue: "Cannot POST /api/auth/signup/"
- Backend server not running
- Solution: Run `python manage.py runserver` in backend directory

### Issue: "Invalid token" error
- Token format incorrect or expired
- Solution: Clear localStorage and login again

### Issue: "Member with this email already exists"
- Email already registered
- Solution: Use a different email address

### Issue: Redirects to login immediately after signup
- Auth state not loading properly
- Solution: Check browser console for errors, clear localStorage

### Issue: "NetworkError when attempting to fetch resource"
- CORS issue or backend not running
- Solution: 
  1. Verify backend is running on http://localhost:8000
  2. Check CORS settings in settings.py
  3. Browser console will show detailed error

---

## Verification Checklist

- [ ] User can signup with email, password
- [ ] User can login with email, password
- [ ] Token is generated and returned after login
- [ ] Token is stored in localStorage
- [ ] Dashboard is protected (requires login)
- [ ] Navigation shows correct info when logged in
- [ ] Logout clears token and redirects to login
- [ ] Error messages display for invalid credentials
- [ ] Form validation works correctly
- [ ] Token persists across page refreshes
- [ ] Protected routes redirect to login if not authenticated
- [ ] Admin credentials work (admin@library.local / admin123)
- [ ] New users can be created via signup
- [ ] API endpoints return tokens
- [ ] Token header format: "Authorization: Token <token>"

---

## Additional Notes

- Tokens are 40-character hexadecimal strings
- Passwords are hashed using PBKDF2 (Django default)
- Email is case-sensitive for login
- All dates are in UTC timezone
- Database uses PostgreSQL by default

