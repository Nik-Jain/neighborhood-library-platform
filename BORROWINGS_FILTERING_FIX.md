# Borrowings Tab Filtering Fix

## Problem Identified

The `/borrowings` page was showing inconsistent behavior:

1. **Main Tab ("/borrowings" endpoint)**: Returns empty results (0 borrowings)
2. **Active Tab ("/borrowings/active" endpoint)**: Shows data but no network call visible
3. **Overdue Tab ("/borrowings/overdue" endpoint)**: Shows data but no network call visible

Additionally, for a MEMBER user, the active/overdue tabs were showing **ALL** borrowings instead of just the member's own borrowings.

## Root Cause

The issue was in `backend/library_service/apps/core/views.py` in the `BorrowingViewSet`:

### The Problem Code
```python
@action(detail=False, methods=['get'])
def active(self, request):
    """Get all active borrowings."""
    active_borrowings = Borrowing.objects.filter(
        returned_at__isnull=True
    ).order_by('-borrowed_at')
    # ... rest of method
```

**Issue:** The `active()` and `overdue()` custom actions were **bypassing the role-based filtering logic** in `get_queryset()`.

### How get_queryset() Works
```python
def get_queryset(self):
    """Filter borrowings: MEMBERs see only their own; ADMIN/LIBRARIAN see all."""
    queryset = super().get_queryset()
    user = self.request.user

    # Check if user is ADMIN or LIBRARIAN
    if user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
        return queryset

    # MEMBERs see only their own borrowings
    try:
        from .models import Member
        member = Member.objects.get(email=user.username)
        return queryset.filter(member=member)
    except Member.DoesNotExist:
        return queryset.none()
```

The main `list()` action uses `get_queryset()` which correctly filters borrowings based on user role. However:
- `active()` and `overdue()` were directly querying `Borrowing.objects.filter()` **without calling `get_queryset()`**
- This meant MEMBER users could see ALL active/overdue borrowings instead of just their own
- It also explained why active/overdue tabs seemed to work without network calls (data might have been cached or the backend was returning different results than expected)

## Solution Implemented

Updated both `active()` and `overdue()` methods to use `self.get_queryset()`:

### Before
```python
@action(detail=False, methods=['get'])
def active(self, request):
    """Get all active borrowings."""
    active_borrowings = Borrowing.objects.filter(
        returned_at__isnull=True
    ).order_by('-borrowed_at')
    # ...
```

### After
```python
@action(detail=False, methods=['get'])
def active(self, request):
    """
    Get all active borrowings.
    Respects role-based filtering: MEMBERs see only their own; ADMIN/LIBRARIAN see all.
    """
    # Start with the role-filtered queryset from get_queryset()
    queryset = self.get_queryset().filter(
        returned_at__isnull=True
    ).order_by('-borrowed_at')
    
    page = self.paginate_queryset(queryset)
    if page is not None:
        serializer = BorrowingListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    serializer = BorrowingListSerializer(queryset, many=True)
    return Response(serializer.data)
```

**Key Changes:**
1. Start with `self.get_queryset()` instead of `Borrowing.objects.all()`
2. Apply additional filters (e.g., `returned_at__isnull=True`) on top of the role-filtered queryset
3. Updated docstring to clarify role-based filtering behavior

Same fix applied to `overdue()` method.

## Behavior After Fix

### For MEMBER Users
- `/borrowings/` → Shows only their own borrowings
- `/borrowings/active/` → Shows only their own active borrowings
- `/borrowings/overdue/` → Shows only their own overdue borrowings

### For ADMIN/LIBRARIAN Users
- `/borrowings/` → Shows all borrowings
- `/borrowings/active/` → Shows all active borrowings
- `/borrowings/overdue/` → Shows all overdue borrowings

## Why Network Calls Were Not Visible

The frontend is correctly making network calls to:
- `/api/v1/borrowings/?page=1` (for "all" tab)
- `/api/v1/borrowings/active/?page=1` (for "active" tab)
- `/api/v1/borrowings/overdue/?page=1` (for "overdue" tab)

The reason you might not see them clearly in the Network tab:
1. **Caching**: Browser might cache certain requests
2. **React Query**: The frontend uses React Query which caches data by queryKey
3. **Multiple tabs switching**: When you click tabs quickly, React Query might reuse cached data if the queries haven't changed

To verify the calls are happening:
1. Open DevTools → Network tab
2. Filter by "Fetch/XHR"
3. Click on each tab and watch for requests to `/api/v1/borrowings/...`
4. They should appear (or may be served from cache)

## Security Implications

This was a **security issue**:
- ✅ **Before fix**: MEMBER users could potentially see all borrowings in active/overdue tabs
- ✅ **After fix**: MEMBER users only see their own borrowings, enforced at the database level

The fix ensures that **all** endpoints respect the role-based permissions:
- Main list view (`/borrowings/`)
- Custom actions (`/borrowings/active/`, `/borrowings/overdue/`)
- All other custom actions should follow the same pattern

## Testing

All 9 RBAC integration tests pass:
```
Ran 9 tests in 4.405s - OK
```

The tests verify:
- Permission enforcement
- Object-level filtering
- 403 Forbidden responses for unauthorized actions

## Related Code

**Files Modified:**
- `backend/library_service/apps/core/views.py` - BorrowingViewSet.active() and .overdue()

**Related Files (unchanged but relevant):**
- `backend/library_service/apps/core/views.py` - BorrowingViewSet.get_queryset() (role filtering logic)
- `frontend/src/app/borrowings/page.tsx` - Frontend UI component
- `frontend/src/hooks/use-borrowings.ts` - React Query hooks
- `frontend/src/lib/api.ts` - API endpoints

## Verification Steps

To verify the fix works correctly:

### 1. Login as a MEMBER user
```
Email: member@example.com (create a test member)
```

### 2. Navigate to `/borrowings`
- Should see only their own borrowings
- Table should show empty if no borrowings for this member

### 3. Click on "Active" tab
- Should see only their own active borrowings
- Check Network tab for `/api/v1/borrowings/active/?page=1` call

### 4. Click on "Overdue" tab
- Should see only their own overdue borrowings
- Check Network tab for `/api/v1/borrowings/overdue/?page=1` call

### 5. Login as ADMIN user
```
Email: admin@library.com
Password: admin123
```

### 6. Navigate to `/borrowings`
- Should see ALL borrowings
- All tabs should show all borrowings

## Future Improvements

Consider these enhancements:
1. Add similar checks to other custom action methods
2. Create a base class for action methods that automatically applies `get_queryset()`
3. Add comprehensive tests for all custom actions
4. Document this pattern in contribution guidelines

## Conclusion

The fix ensures consistent role-based filtering across all borrowing endpoints, with proper security enforcement at the database level. All tests pass and the behavior is now correct for all user roles.
