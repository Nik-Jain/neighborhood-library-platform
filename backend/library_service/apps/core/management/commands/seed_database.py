"""
Management command to seed the database with sample data.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from library_service.apps.core.models import Member, Book, Borrowing, Fine


class Command(BaseCommand):
    help = 'Seeds the database with sample data'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker('en_IN')
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Create superuser
        self._create_superuser()
        
        # Create sample members
        members = self._create_members(10)
        self.stdout.write(self.style.SUCCESS(f'Created {len(members)} members'))
        
        # Create sample books
        books = self._create_books(20)
        self.stdout.write(self.style.SUCCESS(f'Created {len(books)} books'))
        
        # Create sample borrowings
        borrowings = self._create_borrowings(members, books)
        self.stdout.write(self.style.SUCCESS(f'Created {len(borrowings)} borrowings'))
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
    
    def _create_superuser(self):
        """Create a superuser if it doesn't exist."""
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@library.local',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('Created superuser: admin'))
        
        # Also create an admin member account for API login
        if not Member.objects.filter(email='admin@library.local').exists():
            admin_member = Member.objects.create(
                first_name='Admin',
                last_name='User',
                email='admin@library.local',
                membership_number='ADMIN-001',
                membership_status='active'
            )
            admin_member.set_password('admin123')
            admin_member.save()
            self.stdout.write(self.style.SUCCESS('Created admin member: admin@library.local'))
    
    def _create_members(self, count=10):
        """Create sample members."""
        members = []
        for i in range(count):
            member, created = Member.objects.get_or_create(
                email=f'member{i}@library.local',
                defaults={
                    'first_name': self.fake.first_name(),
                    'last_name': self.fake.last_name(),
                    'phone': self.fake.phone_number(),
                    'address': self.fake.address(),
                    'membership_number': f'MEM{i:05d}',
                    'membership_status': 'active'
                }
            )
            if created:
                # Set password for new members
                member.set_password('password123')
                member.save()
                members.append(member)
        
        return members
    
    def _create_books(self, count=20):
        """Create sample books."""
        books = []
        authors = [
            'George Orwell', 'Jane Austen', 'Harper Lee', 'F. Scott Fitzgerald',
            'Mark Twain', 'Stephen King', 'J.K. Rowling', 'J.R.R. Tolkien',
            'Isaac Asimov', 'Arthur C. Clarke'
        ]
        
        titles = [
            '1984', 'Pride and Prejudice', 'To Kill a Mockingbird', 'The Great Gatsby',
            'The Adventures of Tom Sawyer', 'The Shining', "Harry Potter and the Philosopher's Stone",
            'The Lord of the Rings', 'Foundation', '2001: A Space Odyssey',
            'The Catcher in the Rye', 'Brave New World', 'The Hobbit', 'Dune',
            'Ender\'s Game', 'The Handmaid\'s Tale', 'Fahrenheit 451', 'Neuromancer',
            'The Foundation\'s Edge', 'A Brief History of Time'
        ]
        
        for i in range(min(count, len(titles))):
            book, created = Book.objects.get_or_create(
                title=titles[i],
                author=authors[i % len(authors)],
                defaults={
                    'publisher': self.fake.company(),
                    'publication_year': int(self.fake.date_between(start_date='-126y', end_date='today').year),
                    'description': self.fake.paragraph(nb_sentences=3),
                    'total_copies': self.fake.random_int(min=1, max=10),
                    'available_copies': self.fake.random_int(min=0, max=10),
                    'condition': self.fake.random_element(['excellent', 'good', 'fair']),
                    'language': 'English'
                }
            )
            if created:
                books.append(book)
        
        return books
    
    def _create_borrowings(self, members, books):
        """Create sample borrowings."""
        borrowings = []
        
        for _ in range(min(15, len(members) * 2)):
            member = self.fake.random_element(members)
            book = self.fake.random_element(books)
            
            # Skip if member already has this book
            if Borrowing.objects.filter(
                member=member,
                book=book,
                returned_at__isnull=True
            ).exists():
                continue
            
            # Create borrowing
            borrowed_at = timezone.now() - timedelta(days=self.fake.random_int(1, 30))
            due_date = (borrowed_at + timedelta(days=14)).date()
            
            borrowing, created = Borrowing.objects.get_or_create(
                member=member,
                book=book,
                borrowed_at=borrowed_at,
                defaults={
                    'due_date': due_date,
                    'notes': self.fake.sentence(),
                }
            )
            
            if created:
                borrowings.append(borrowing)
                
                # Randomly mark some as returned
                if self.fake.boolean(chance_of_getting_true=50):
                    returned_at = borrowed_at + timedelta(
                        days=self.fake.random_int(1, 25)
                    )
                    borrowing.returned_at = returned_at
                    borrowing.save()
                    
                    # Update book availability
                    borrowing.book.available_copies += 1
                    borrowing.book.save()
                    
                    # Create fine if overdue
                    if returned_at.date() > due_date:
                        days_overdue = (returned_at.date() - due_date).days
                        Fine.objects.create(
                            borrowing=borrowing,
                            amount=Decimal(days_overdue * 0.50),
                            reason=f'Overdue by {days_overdue} days'
                        )
        
        return borrowings
