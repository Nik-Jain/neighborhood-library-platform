# Database Seeding Information

## Overview
The `seed_database.py` management command has been updated to create a realistic dataset for testing and development purposes.

## Database Statistics

After running the seed command, you should have:

- **38+ Members** (including admin and librarian accounts)
  - 1 Admin account
  - 2 Librarian accounts
  - 30+ Regular member accounts
  - Mix of active and suspended statuses

- **60+ Books** 
  - Diverse collection of classic and modern literature
  - Fiction, Non-Fiction, Science Fiction, Fantasy, Horror, etc.
  - Multiple copies of popular books
  - Varied conditions (excellent, good, fair)

- **70+ Borrowings**
  - Mix of active and returned borrowings
  - Realistic borrowing dates (spanning last 90 days)
  - ~30% active borrowings, ~70% returned

- **40+ Fines**
  - Overdue fines
  - Damage fines
  - Lost book fines
  - Mix of paid and unpaid fines

## Running the Seed Command

```bash
cd backend
python manage.py seed_database
```

The command is idempotent - it can be run multiple times without creating duplicates. It will:
- Ensure RBAC groups (ADMIN, LIBRARIAN, MEMBER) exist
- Create or reuse existing accounts
- Create new books if they don't exist
- Create additional borrowings and fines

## Test Account Credentials

### Admin Account
- **Email**: `admin@library.local`
- **Password**: `admin123`
- **Membership Number**: `ADMIN-001`

### Librarian Accounts
1. **Email**: `librarian1@library.local`
   - **Password**: `librarian123`
   - **Membership Number**: `LIB-001`

2. **Email**: `librarian2@library.local`
   - **Password**: `librarian123`
   - **Membership Number**: `LIB-002`

### Member Accounts
- **Email Pattern**: `member1@library.local` to `member30@library.local`
- **Password**: `password123` (same for all members)
- **Membership Numbers**: `MEM-00001` to `MEM-00030`

## Book Collection

The seeded database includes 60+ books from various genres:

### Categories Include:
- **Classic Literature**: 1984, Pride and Prejudice, To Kill a Mockingbird, etc.
- **Fantasy**: Harry Potter series, Lord of the Rings, The Hobbit, etc.
- **Science Fiction**: Dune, Foundation, The Martian, Neuromancer, etc.
- **Horror**: Stephen King collection (The Shining, It, Carrie, etc.)
- **Dystopian Fiction**: The Hunger Games, Brave New World, Fahrenheit 451, etc.
- **Thriller**: The Da Vinci Code, Gone Girl, etc.
- **Non-Fiction**: Sapiens, A Brief History of Time, etc.

## Key Features

1. **Realistic User Distribution**
   - Admin, Librarian, and Member roles properly assigned
   - Users linked to Django User model for authentication
   - RBAC groups automatically assigned via signals

2. **Diverse Book Inventory**
   - Multiple copies of popular titles
   - Varied publication years (1920-2024)
   - Different conditions and languages
   - ISBN numbers generated

3. **Active Library Operations**
   - Mix of current and historical borrowings
   - Realistic borrowing patterns (14-day periods)
   - Overdue scenarios with fines
   - Damage and lost book fines

4. **Data Integrity**
   - Book availability counts properly maintained
   - Fines linked to borrowings
   - Membership statuses (mostly active, some suspended)
   - Proper date ranges for realistic testing

## Resetting the Database

If you need to start fresh:

```bash
cd backend
python manage.py flush --no-input
python manage.py migrate
python manage.py seed_database
```

## Development Notes

- The seed command uses **Faker** library for generating realistic Indian names and addresses
- Groups are created automatically using `ensure_roles_exist()` utility
- Member-User synchronization handled via Django signals
- All passwords are properly hashed using Django's password hashing
