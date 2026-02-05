"""
Comprehensive tests for borrowing service.

Tests for:
- Transactional consistency
- Concurrency safety
- Error handling
- Edge cases
"""
from django.test import TestCase, TransactionTestCase
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from decimal import Decimal
from threading import Thread
from time import sleep
import uuid

from .models import Member, Book, Borrowing, Fine
from .services import BorrowingService
from .exceptions import (
    MemberNotFoundException,
    BookNotFoundException,
    BorrowingNotFoundException,
    MemberNotActiveException,
    BookNotAvailableException,
    BookAlreadyBorrowedException,
    BorrowingAlreadyReturnedException,
    ConcurrencyException,
)


class BorrowingServiceTests(TestCase):
    """Test cases for BorrowingService transactional operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            membership_number='MEM001',
            membership_status='active'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            total_copies=5,
            available_copies=5
        )
    
    def test_create_borrowing_success(self):
        """Test successful borrowing creation."""
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        self.assertIsNotNone(borrowing)
        self.assertEqual(borrowing.member, self.member)
        self.assertEqual(borrowing.book, self.book)
        self.assertIsNone(borrowing.returned_at)
        
        # Verify book availability was decremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
    
    def test_create_borrowing_member_not_found(self):
        """Test borrowing fails when member doesn't exist."""
        fake_member_id = uuid.uuid4()
        
        with self.assertRaises(MemberNotFoundException):
            BorrowingService.create_borrowing(
                member_id=fake_member_id,
                book_id=self.book.id
            )
    
    def test_create_borrowing_book_not_found(self):
        """Test borrowing fails when book doesn't exist."""
        fake_book_id = uuid.uuid4()
        
        with self.assertRaises(BookNotFoundException):
            BorrowingService.create_borrowing(
                member_id=self.member.id,
                book_id=fake_book_id
            )
    
    def test_create_borrowing_inactive_member(self):
        """Test borrowing fails for inactive member."""
        self.member.membership_status = 'suspended'
        self.member.save()
        
        with self.assertRaises(MemberNotActiveException):
            BorrowingService.create_borrowing(
                member_id=self.member.id,
                book_id=self.book.id
            )
        
        # Verify no book was decremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 5)
    
    def test_create_borrowing_no_available_copies(self):
        """Test borrowing fails when no copies available."""
        self.book.available_copies = 0
        self.book.save()
        
        with self.assertRaises(BookNotAvailableException):
            BorrowingService.create_borrowing(
                member_id=self.member.id,
                book_id=self.book.id
            )
    
    def test_create_borrowing_duplicate_active(self):
        """Test borrowing fails if member already has the book."""
        # Create first borrowing
        BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        # Attempt second borrowing of same book
        with self.assertRaises(BookAlreadyBorrowedException):
            BorrowingService.create_borrowing(
                member_id=self.member.id,
                book_id=self.book.id
            )
        
        # Verify only one copy was decremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)
    
    def test_return_borrowing_success(self):
        """Test successful book return."""
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        returned_borrowing, fine = BorrowingService.return_borrowing(borrowing.id)
        
        self.assertIsNotNone(returned_borrowing.returned_at)
        self.assertIsNone(fine)  # No fine if not overdue
        
        # Verify book availability was incremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 5)
    
    def test_return_borrowing_not_found(self):
        """Test returning non-existent borrowing raises error."""
        fake_borrowing_id = uuid.uuid4()
        
        with self.assertRaises(BorrowingNotFoundException):
            BorrowingService.return_borrowing(fake_borrowing_id)
    
    def test_return_borrowing_with_fine(self):
        """Test book return creates fine for overdue."""
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        # Set due date in the past
        borrowing.due_date = timezone.now().date() - timedelta(days=5)
        borrowing.save()
        
        returned_borrowing, fine = BorrowingService.return_borrowing(borrowing.id)
        
        self.assertIsNotNone(fine)
        self.assertEqual(fine.amount, Decimal('5.00'))  # 5 days * $1/day
        self.assertFalse(fine.is_paid)
        self.assertIn('5 days', fine.reason)
    
    def test_return_borrowing_already_returned(self):
        """Test returning already returned book raises error."""
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        # Return once
        BorrowingService.return_borrowing(borrowing.id)
        
        # Attempt to return again
        with self.assertRaises(BorrowingAlreadyReturnedException):
            BorrowingService.return_borrowing(borrowing.id)
        
        # Verify book availability not double-incremented
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 5)
    
    def test_borrowing_transaction_rollback_on_error(self):
        """Test transaction rolls back if error occurs."""
        from unittest.mock import patch, MagicMock
        
        # Save initial state
        initial_count = Borrowing.objects.count()
        initial_available = self.book.available_copies
        
        # Mock Borrowing.save() to fail AFTER the book update has occurred
        # This simulates a database error during borrowing creation
        original_save = Borrowing.save
        
        def failing_save(self, *args, **kwargs):
            raise Exception("Simulated database error during save")
        
        with patch.object(Borrowing, 'save', failing_save):
            with self.assertRaises(Exception) as context:
                BorrowingService.create_borrowing(
                    member_id=self.member.id,
                    book_id=self.book.id
                )
            self.assertIn("database error", str(context.exception).lower())
        
        # Verify transaction rolled back - book copies should be unchanged
        self.book.refresh_from_db()
        self.assertEqual(
            Borrowing.objects.count(),
            initial_count,
            "No borrowing should be created after transaction failure"
        )
        self.assertEqual(
            self.book.available_copies,
            initial_available,
            "Book copies should be rolled back after transaction failure"
        )
    
    def test_fine_calculation(self):
        """Test fine calculation for different overdue periods."""
        self.assertEqual(
            BorrowingService.calculate_fine_amount(0),
            Decimal('0.00')
        )
        self.assertEqual(
            BorrowingService.calculate_fine_amount(1),
            Decimal('1.00')
        )
        self.assertEqual(
            BorrowingService.calculate_fine_amount(10),
            Decimal('10.00')
        )
        self.assertEqual(
            BorrowingService.calculate_fine_amount(-5),
            Decimal('0.00')  # Negative days should return 0
        )
    
    def test_duplicate_fine_prevented(self):
        """Test that duplicate fines for same borrowing are prevented."""
        # Create overdue borrowing
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id,
            due_date=(timezone.now().date() - timedelta(days=5))
        )
        
        # Return and create fine
        returned_borrowing, fine = BorrowingService.return_borrowing(borrowing.id)
        self.assertIsNotNone(fine)
        self.assertEqual(fine.amount, Decimal('5.00'))
        
        # Attempt to create another fine manually - should be prevented by constraint
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Fine.objects.create(
                borrowing=borrowing,
                amount=Decimal('10.00'),
                reason='Duplicate attempt'
            )


class BorrowingConcurrencyTests(TransactionTestCase):
    """Test cases for concurrent borrowing operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.member1 = Member.objects.create(
            first_name='Member',
            last_name='One',
            email='member1@example.com',
            membership_number='MEM001',
            membership_status='active'
        )
        
        self.member2 = Member.objects.create(
            first_name='Member',
            last_name='Two',
            email='member2@example.com',
            membership_number='MEM002',
            membership_status='active'
        )
        
        self.book = Book.objects.create(
            title='Last Copy',
            author='Author',
            total_copies=1,
            available_copies=1
        )
    
    def test_concurrent_borrowing_last_copy(self):
        """
        Test concurrent attempts to borrow last copy.
        
        Uses barrier to ensure threads execute simultaneously.
        """
        from threading import Barrier
        
        results = {'success': [], 'errors': [], 'barrier': Barrier(2)}
        
        def borrow_book(member_id, book_id, results_dict):
            """Helper function to borrow in thread with synchronization."""
            try:
                # Wait for both threads to reach this point
                results_dict['barrier'].wait()
                
                # Now both threads try to borrow simultaneously
                borrowing = BorrowingService.create_borrowing(
                    member_id=member_id,
                    book_id=book_id
                )
                results_dict['success'].append(str(borrowing.id))
            except (BookNotAvailableException, ConcurrencyException) as e:
                results_dict['errors'].append(str(e))
            except Exception as e:
                # Catch any unexpected errors
                results_dict['errors'].append(f"Unexpected: {str(e)}")
        
        # Create threads to borrow simultaneously
        thread1 = Thread(
            target=borrow_book,
            args=(self.member1.id, self.book.id, results)
        )
        thread2 = Thread(
            target=borrow_book,
            args=(self.member2.id, self.book.id, results)
        )
        
        # Start both threads
        thread1.start()
        thread2.start()
        
        # Wait for completion
        thread1.join(timeout=5)
        thread2.join(timeout=5)
        
        # Verify exactly one succeeded
        self.assertEqual(
            len(results['success']), 1,
            f"Expected 1 success, got {len(results['success'])}: {results}"
        )
        self.assertEqual(
            len(results['errors']), 1,
            f"Expected 1 error, got {len(results['errors'])}: {results}"
        )
        
        # Verify book state is correct
        self.book.refresh_from_db()
        self.assertEqual(
            self.book.available_copies, 0,
            "Book should have 0 available copies"
        )
        
        # Verify only one borrowing was created
        self.assertEqual(
            Borrowing.objects.filter(book=self.book, returned_at__isnull=True).count(),
            1,
            "Should have exactly 1 active borrowing"
        )


class BorrowingAPIIntegrationTests(APITestCase):
    """Integration tests for borrowing API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create groups
        admin_group = Group.objects.create(name='ADMIN')
        librarian_group = Group.objects.create(name='LIBRARIAN')
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@example.com',
            password='adminpass123'
        )
        self.admin_user.groups.add(admin_group)
        
        # Create member
        self.member = Member.objects.create(
            first_name='Test',
            last_name='Member',
            email='member@example.com',
            membership_number='MEM001',
            membership_status='active'
        )
        
        # Create book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            total_copies=3,
            available_copies=3
        )
        
        # Authenticate as admin
        self.client.force_authenticate(user=self.admin_user)
    
    def test_create_borrowing_api(self):
        """Test creating borrowing via API."""
        data = {
            'member_id': str(self.member.id),
            'book_id': str(self.book.id),
        }
        
        response = self.client.post('/api/v1/borrowings/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        
        # Verify database state
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 2)
    
    def test_create_borrowing_no_available_copies(self):
        """Test API error when no copies available."""
        self.book.available_copies = 0
        self.book.save()
        
        data = {
            'member_id': str(self.member.id),
            'book_id': str(self.book.id),
        }
        
        response = self.client.post('/api/v1/borrowings/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_return_book_api(self):
        """Test returning book via API."""
        # Create borrowing
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        # Return via API
        response = self.client.post(
            f'/api/v1/borrowings/{borrowing.id}/return_book/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['returned_at'])
        
        # Verify database state
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 3)
    
    def test_return_book_with_overdue_fine(self):
        """Test API creates fine for overdue return."""
        # Create borrowing
        borrowing = BorrowingService.create_borrowing(
            member_id=self.member.id,
            book_id=self.book.id
        )
        
        # Make it overdue
        borrowing.due_date = timezone.now().date() - timedelta(days=3)
        borrowing.save()
        
        # Return via API
        response = self.client.post(
            f'/api/v1/borrowings/{borrowing.id}/return_book/'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify fine created
        fine = Fine.objects.filter(borrowing=borrowing).first()
        self.assertIsNotNone(fine)
        self.assertEqual(fine.amount, Decimal('3.00'))


class BookConstraintTests(TestCase):
    """Test database constraints on Book model."""
    
    def test_available_copies_cannot_exceed_total(self):
        """Test constraint prevents available > total copies."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title='Invalid Book',
                author='Author',
                total_copies=5,
                available_copies=10  # Invalid: more than total
            )
    
    def test_negative_copies_prevented(self):
        """Test constraint prevents negative copies."""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title='Invalid Book',
                author='Author',
                total_copies=-1,  # Invalid: negative
                available_copies=0
            )


class BorrowingConstraintTests(TestCase):
    """Test database constraints on Borrowing model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.member = Member.objects.create(
            first_name='Test',
            last_name='Member',
            email='test@example.com',
            membership_number='MEM001'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Author',
            total_copies=5,
            available_copies=5
        )
    
    def test_unique_active_borrowing_constraint(self):
        """Test constraint prevents duplicate active borrowings."""
        from django.db import IntegrityError
        
        # Create first borrowing
        Borrowing.objects.create(
            member=self.member,
            book=self.book,
            due_date=timezone.now().date() + timedelta(days=14)
        )
        
        # Attempt to create duplicate active borrowing
        with self.assertRaises(IntegrityError):
            Borrowing.objects.create(
                member=self.member,
                book=self.book,
                due_date=timezone.now().date() + timedelta(days=14)
            )
    
    def test_can_borrow_same_book_after_return(self):
        """Test member can borrow same book after returning."""
        # Create and return first borrowing
        borrowing1 = Borrowing.objects.create(
            member=self.member,
            book=self.book,
            due_date=timezone.now().date() + timedelta(days=14)
        )
        borrowing1.returned_at = timezone.now()
        borrowing1.save()
        
        # Should be able to borrow again
        borrowing2 = Borrowing.objects.create(
            member=self.member,
            book=self.book,
            due_date=timezone.now().date() + timedelta(days=14)
        )
        
        self.assertIsNotNone(borrowing2)
        self.assertNotEqual(borrowing1.id, borrowing2.id)
