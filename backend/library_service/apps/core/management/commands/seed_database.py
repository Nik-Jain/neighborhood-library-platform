"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from faker import Faker
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
import random
import os

from library_service.apps.core.models import Member, Book, Borrowing, Fine


class Command(BaseCommand):
    help = 'Seeds the database with sample data'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker('en_IN')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Ensure RBAC groups exist
        self._ensure_groups()
        
        # Production: create only admin (and required groups), then return
        if self._is_production_environment():
            # Explicitly ensure all required groups exist
            Group.objects.get_or_create(name='ADMIN')
            Group.objects.get_or_create(name='LIBRARIAN')
            Group.objects.get_or_create(name='MEMBER')
            self._create_superuser()
            self._create_admin_member_only()
            self.stdout.write(self.style.SUCCESS('Production mode: admin created, skipping full seeding'))
            return
        
        # Non-production: create superuser and full seed data
        self._create_superuser()
        
        # Create admin and librarian members
        admin_members = self._create_admin_members()
        self.stdout.write(self.style.SUCCESS(f'Created {len(admin_members)} admin/librarian accounts'))
        
        # Create sample members (at least 30 total)
        members = self._create_members(30)
        self.stdout.write(self.style.SUCCESS(f'Created {len(members)} member accounts'))
        
        # Combine all members for borrowings (get all existing members from DB)
        all_members = list(Member.objects.all())
        if not all_members:
            self.stdout.write(self.style.ERROR('No members found in database!'))
            return
        
        # Create sample books (at least 50)
        books = self._create_books(60)
        self.stdout.write(self.style.SUCCESS(f'Created {len(books)} books'))
        
        # Get all books from database
        all_books = list(Book.objects.all())
        if not all_books:
            self.stdout.write(self.style.ERROR('No books found in database!'))
            return
        
        # Create sample borrowings (at least 50)
        borrowings = self._create_borrowings(all_members, all_books, 70)
        self.stdout.write(self.style.SUCCESS(f'Created {len(borrowings)} borrowings'))
        
        # Create additional fines for some borrowings
        fines = self._create_additional_fines(borrowings)
        self.stdout.write(self.style.SUCCESS(f'Created total fines for {fines} borrowings'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))

    def _is_production_environment(self):
        """Return True if environment is production."""
        env_value = os.environ.get('DJANGO_ENV', 'development').strip().lower()
        return env_value == 'production'
    
    def _ensure_groups(self):
        """Ensure all required groups/roles exist."""
        try:
            from library_service.apps.core.utils import ensure_roles_exist
            ensure_roles_exist()
            self.stdout.write(self.style.SUCCESS('Ensured all RBAC groups exist'))
        except Exception as e:
            # Manually create groups if utility function fails
            Group.objects.get_or_create(name='ADMIN')
            Group.objects.get_or_create(name='LIBRARIAN')
            Group.objects.get_or_create(name='MEMBER')
            self.stdout.write(self.style.WARNING(f'Manually created groups: {e}'))
    
    def _create_superuser(self):
        """Create a Django superuser if it doesn't exist."""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@library.local',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created Django superuser: admin'))

        # Ensure superuser is in ADMIN group
        try:
            admin_user = User.objects.filter(username='admin').first()
            if admin_user:
                admin_group, _ = Group.objects.get_or_create(name='ADMIN')
                admin_user.groups.add(admin_group)
                admin_user.save()
        except Exception:
            pass
    
    def _create_admin_members(self):
        """Create admin and librarian member accounts."""
        admin_members = []
        
        # Create Admin Member
        existing_admin = Member.objects.filter(email='admin@library.local').first()
        if existing_admin:
            admin_members.append(existing_admin)
        else:
            admin_member = Member.objects.create(
                first_name='Admin',
                last_name='User',
                email='admin@library.local',
                phone='+91-9876543210',
                address='Library Headquarters, Delhi',
                membership_number='ADMIN-001',
                membership_status='active'
            )
            admin_member.set_password('admin123')
            admin_member.save()
            
            # Add to ADMIN group via User object (signal creates User)
            admin_group, _ = Group.objects.get_or_create(name='ADMIN')
            user = User.objects.filter(username='admin@library.local').first()
            if user:
                user.groups.add(admin_group)
                user.save()
            
            admin_members.append(admin_member)
            self.stdout.write(self.style.SUCCESS('Created admin member: admin@library.local'))
        
        # Create Librarian Members (2-3)
        librarian_emails = [
            'librarian1@library.local',
            'librarian2@library.local',
        ]
        
        for idx, email in enumerate(librarian_emails, 1):
            existing_lib = Member.objects.filter(email=email).first()
            if existing_lib:
                admin_members.append(existing_lib)
            else:
                librarian = Member.objects.create(
                    first_name=self.fake.first_name(),
                    last_name=self.fake.last_name(),
                    email=email,
                    phone=self.fake.phone_number(),
                    address=self.fake.address(),
                    membership_number=f'LIB-{idx:03d}',
                    membership_status='active'
                )
                librarian.set_password('librarian123')
                librarian.save()
                
                # Add to LIBRARIAN group via User object (signal creates User)
                librarian_group, _ = Group.objects.get_or_create(name='LIBRARIAN')
                user = User.objects.filter(username=email).first()
                if user:
                    user.groups.add(librarian_group)
                    user.save()
                
                admin_members.append(librarian)
                self.stdout.write(self.style.SUCCESS(f'Created librarian: {email}'))
        
        return admin_members

    def _create_admin_member_only(self):
        """Create only the admin member account (no librarians)."""
        # Reuse the admin creation logic from _create_admin_members without librarians
        existing_admin = Member.objects.filter(email='admin@library.local').first()
        if existing_admin:
            return existing_admin

        admin_member = Member.objects.create(
            first_name='Admin',
            last_name='User',
            email='admin@library.local',
            phone='+91-9876543210',
            address='Library Headquarters, Delhi',
            membership_number='ADMIN-001',
            membership_status='active'
        )
        admin_member.set_password('admin123')
        admin_member.save()

        admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        user = User.objects.filter(username='admin@library.local').first()
        if user:
            user.groups.add(admin_group)
            user.save()

        self.stdout.write(self.style.SUCCESS('Created admin member: admin@library.local'))
        return admin_member
    
    def _create_members(self, count=30):
        """Create sample member accounts."""
        members = []
        member_group, _ = Group.objects.get_or_create(name='MEMBER')
        
        for i in range(count):
            email = f'member{i+1}@library.local'
            
            existing = Member.objects.filter(email=email).first()
            if existing:
                members.append(existing)
                continue
                
            member = Member.objects.create(
                email=email,
                first_name=self.fake.first_name(),
                last_name=self.fake.last_name(),
                phone=self.fake.phone_number(),
                address=self.fake.address(),
                membership_number=f'MEM-{i+1:05d}',
                membership_status=random.choice(['active', 'active', 'active', 'suspended'])  # Mostly active
            )
            # Set password for new members
            member.set_password('password123')
            member.save()
            
            # Add to MEMBER group via User object (signal creates User)
            # Note: The signal already assigns MEMBER group, but we do it explicitly
            user = User.objects.filter(username=email).first()
            if user:
                user.groups.add(member_group)
                user.save()
            
            members.append(member)
        
        return members
    
    def _create_books(self, count=60):
        """Create sample books with diverse categories."""
        books = []
        
        # Expanded book data for realistic seeding
        book_data = [
            ('1984', 'George Orwell', 'Dystopian Fiction'),
            ('Pride and Prejudice', 'Jane Austen', 'Romance'),
            ('To Kill a Mockingbird', 'Harper Lee', 'Classic Literature'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic Literature'),
            ('The Adventures of Tom Sawyer', 'Mark Twain', 'Adventure'),
            ('The Shining', 'Stephen King', 'Horror'),
            ("Harry Potter and the Philosopher's Stone", 'J.K. Rowling', 'Fantasy'),
            ('The Lord of the Rings', 'J.R.R. Tolkien', 'Fantasy'),
            ('Foundation', 'Isaac Asimov', 'Science Fiction'),
            ('2001: A Space Odyssey', 'Arthur C. Clarke', 'Science Fiction'),
            ('The Catcher in the Rye', 'J.D. Salinger', 'Classic Literature'),
            ('Brave New World', 'Aldous Huxley', 'Dystopian Fiction'),
            ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy'),
            ('Dune', 'Frank Herbert', 'Science Fiction'),
            ("Ender's Game", 'Orson Scott Card', 'Science Fiction'),
            ("The Handmaid's Tale", 'Margaret Atwood', 'Dystopian Fiction'),
            ('Fahrenheit 451', 'Ray Bradbury', 'Dystopian Fiction'),
            ('Neuromancer', 'William Gibson', 'Cyberpunk'),
            ('A Brief History of Time', 'Stephen Hawking', 'Non-Fiction'),
            ('Sapiens', 'Yuval Noah Harari', 'Non-Fiction'),
            ('The Da Vinci Code', 'Dan Brown', 'Thriller'),
            ('Angels & Demons', 'Dan Brown', 'Thriller'),
            ('The Alchemist', 'Paulo Coelho', 'Philosophy'),
            ('Life of Pi', 'Yann Martel', 'Adventure'),
            ('The Kite Runner', 'Khaled Hosseini', 'Drama'),
            ('The Book Thief', 'Markus Zusak', 'Historical Fiction'),
            ('The Hunger Games', 'Suzanne Collins', 'Dystopian Fiction'),
            ('Twilight', 'Stephenie Meyer', 'Romance'),
            ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Mystery'),
            ('Gone Girl', 'Gillian Flynn', 'Thriller'),
            ('The Fault in Our Stars', 'John Green', 'Young Adult'),
            ('Divergent', 'Veronica Roth', 'Dystopian Fiction'),
            ('The Maze Runner', 'James Dashner', 'Young Adult'),
            ('Ready Player One', 'Ernest Cline', 'Science Fiction'),
            ('The Martian', 'Andy Weir', 'Science Fiction'),
            ('Station Eleven', 'Emily St. John Mandel', 'Science Fiction'),
            ('The Road', 'Cormac McCarthy', 'Post-Apocalyptic'),
            ('The Stand', 'Stephen King', 'Horror'),
            ('It', 'Stephen King', 'Horror'),
            ('Carrie', 'Stephen King', 'Horror'),
            ('The Green Mile', 'Stephen King', 'Drama'),
            ('Misery', 'Stephen King', 'Horror'),
            ('Pet Sematary', 'Stephen King', 'Horror'),
            ('The Dark Tower', 'Stephen King', 'Fantasy'),
            ('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy'),
            ('Mistborn', 'Brandon Sanderson', 'Fantasy'),
            ('The Way of Kings', 'Brandon Sanderson', 'Fantasy'),
            ('A Game of Thrones', 'George R.R. Martin', 'Fantasy'),
            ('The Silmarillion', 'J.R.R. Tolkien', 'Fantasy'),
            ('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy'),
            ('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 'Fantasy'),
            ('Harry Potter and the Goblet of Fire', 'J.K. Rowling', 'Fantasy'),
            ('The Chronicles of Narnia', 'C.S. Lewis', 'Fantasy'),
            ('Alice in Wonderland', 'Lewis Carroll', 'Fantasy'),
            ('Animal Farm', 'George Orwell', 'Political Satire'),
            ('Lord of the Flies', 'William Golding', 'Classic Literature'),
            ('Of Mice and Men', 'John Steinbeck', 'Classic Literature'),
            ('The Grapes of Wrath', 'John Steinbeck', 'Classic Literature'),
            ('Moby Dick', 'Herman Melville', 'Classic Literature'),
            ('War and Peace', 'Leo Tolstoy', 'Classic Literature'),
            ('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic Literature'),
            ('The Brothers Karamazov', 'Fyodor Dostoevsky', 'Classic Literature'),
            ('Anna Karenina', 'Leo Tolstoy', 'Classic Literature'),
            ('One Hundred Years of Solitude', 'Gabriel García Márquez', 'Magical Realism'),
            ('Love in the Time of Cholera', 'Gabriel García Márquez', 'Romance'),
        ]
        
        for i in range(min(count, len(book_data))):
            title, author, _ = book_data[i]  # category unused for now
            
            existing_book = Book.objects.filter(title=title, author=author).first()
            if existing_book:
                books.append(existing_book)
                continue
            
            total_copies = random.randint(2, 10)
            available_copies = random.randint(0, total_copies)
            
            book = Book.objects.create(
                title=title,
                author=author,
                publisher=self.fake.company(),
                publication_year=random.randint(1920, 2024),
                isbn=self.fake.isbn13(),
                description=self.fake.paragraph(nb_sentences=5),
                total_copies=total_copies,
                available_copies=available_copies,
                condition=random.choice(['excellent', 'excellent', 'good', 'good', 'fair']),
                language=random.choice(['English', 'English', 'English', 'Hindi', 'Spanish'])
            )
            books.append(book)
        
        return books
    
    def _create_borrowings(self, members, books, count=70):
        """Create sample borrowings with realistic patterns."""
        borrowings = []
        created_count = 0
        attempts = 0
        max_attempts = count * 3  # Prevent infinite loops
        
        while created_count < count and attempts < max_attempts:
            attempts += 1
            
            member = random.choice(members)
            book = random.choice(books)
            
            # Skip if member already has an active borrowing of this book
            if Borrowing.objects.filter(
                member=member,
                book=book,
                returned_at__isnull=True
            ).exists():
                continue
            
            # Create borrowing with varied dates
            days_ago = random.randint(1, 90)
            borrowed_at = timezone.now() - timedelta(days=days_ago)
            due_date = (borrowed_at + timedelta(days=14)).date()
            
            borrowing = Borrowing.objects.create(
                member=member,
                book=book,
                borrowed_at=borrowed_at,
                due_date=due_date,
                notes=self.fake.sentence() if random.random() > 0.5 else ''
            )
            
            borrowings.append(borrowing)
            created_count += 1
            
            # Decrease available copies
            if book.available_copies > 0:
                book.available_copies -= 1
                book.save()
            
            # Randomly mark some as returned (70% returned, 30% active)
            if random.random() < 0.7:
                # Return date could be on time, early, or late
                days_borrowed = random.randint(1, 30)
                returned_at = borrowed_at + timedelta(days=days_borrowed)
                borrowing.returned_at = returned_at
                borrowing.save()
                
                # Update book availability
                borrowing.book.available_copies += 1
                borrowing.book.save()
                
                # Create fine if overdue
                if returned_at.date() > due_date:
                    days_overdue = (returned_at.date() - due_date).days
                    fine_amount = Decimal(str(days_overdue * 0.50))
                    
                    is_paid = random.choice([False, False, True])  # Mostly unpaid
                    fine = Fine.objects.create(
                        borrowing=borrowing,
                        amount=fine_amount,
                        reason=f'Overdue by {days_overdue} days',
                        is_paid=is_paid,
                        paid_at=returned_at + timedelta(days=random.randint(1, 5)) if is_paid else None
                    )
        
        return borrowings
    
    def _create_additional_fines(self, borrowings):
        """Create additional fines for some borrowings (damage, lost book, etc)."""
        fine_count = 0
        
        # Add damage or lost book fines for some borrowings
        sample_borrowings = random.sample(
            borrowings, 
            min(10, len(borrowings))  # Add fines to ~10 random borrowings
        )
        
        for borrowing in sample_borrowings:
            # Skip if borrowing already has a fine
            if Fine.objects.filter(borrowing=borrowing).exists():
                continue
            
            fine_type = random.choice(['damage', 'damage', 'lost'])
            
            if fine_type == 'damage':
                amount = Decimal(random.uniform(10, 100))
                reason = random.choice([
                    'Book damaged - water damage',
                    'Book damaged - torn pages',
                    'Book damaged - cover torn',
                    'Book damaged - writing in book'
                ])
            else:  # lost
                amount = Decimal(random.uniform(100, 500))
                reason = 'Book lost by member'
            
            is_paid = random.choice([False, False, True])  # Mostly unpaid
            Fine.objects.create(
                borrowing=borrowing,
                amount=amount,
                reason=reason,
                is_paid=is_paid
            )
            fine_count += 1
        
        return fine_count
