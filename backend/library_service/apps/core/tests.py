"""
Tests for the core library service application.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
from django.utils import timezone

from .models import Member, Book, Borrowing, Fine


class MemberModelTests(TestCase):
    """Test cases for the Member model."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            membership_number='MEM001'
        )
    
    def test_create_member(self):
        """Test creating a member."""
        self.assertEqual(self.member.full_name, 'John Doe')
        self.assertEqual(self.member.membership_status, 'active')
    
    def test_member_str(self):
        """Test member string representation."""
        self.assertEqual(str(self.member), 'John Doe')


class BookModelTests(TestCase):
    """Test cases for the Book model."""
    
    def setUp(self):
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            total_copies=5,
            available_copies=5
        )
    
    def test_create_book(self):
        """Test creating a book."""
        self.assertEqual(self.book.title, 'Test Book')
        self.assertTrue(self.book.is_available)
    
    def test_book_availability(self):
        """Test book availability check."""
        self.assertTrue(self.book.is_available)
        self.book.available_copies = 0
        self.book.save()
        self.assertFalse(self.book.is_available)


class BorrowingModelTests(TestCase):
    """Test cases for the Borrowing model."""
    
    def setUp(self):
        self.member = Member.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            membership_number='MEM002'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            total_copies=1,
            available_copies=1
        )
        self.borrowing = Borrowing.objects.create(
            member=self.member,
            book=self.book
        )
    
    def test_create_borrowing(self):
        """Test creating a borrowing record."""
        self.assertEqual(self.borrowing.status, 'active')
        self.assertFalse(self.borrowing.is_overdue)
    
    def test_overdue_detection(self):
        """Test overdue detection."""
        self.borrowing.due_date = timezone.now().date() - timedelta(days=1)
        self.borrowing.save()
        self.assertTrue(self.borrowing.is_overdue)
    
    def test_return_book(self):
        """Test returning a book."""
        self.borrowing.returned_at = timezone.now()
        self.borrowing.save()
        self.assertEqual(self.borrowing.status, 'returned')


class MemberAPITests(APITestCase):
    """Test cases for Member API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.member = Member.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            membership_number='MEM003'
        )
    
    def test_list_members(self):
        """Test listing members."""
        response = self.client.get('/api/v1/members/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_member(self):
        """Test creating a member via API."""
        # Assign admin role to user for member creation
        from library_service.apps.core.models import UserRole
        UserRole.objects.create(user=self.user, role='ADMIN')
        
        data = {
            'first_name': 'New',
            'last_name': 'Member',
            'email': 'new@example.com',
            'membership_number': 'MEM004'
        }
        response = self.client.post('/api/v1/members/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BookAPITests(APITestCase):
    """Test cases for Book API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author'
        )
    
    def test_list_books(self):
        """Test listing books."""
        response = self.client.get('/api/v1/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BorrowingAPITests(APITestCase):
    """Test cases for Borrowing API endpoints."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.member = Member.objects.create(
            first_name='Test',
            last_name='User',
            email='test@example.com',
            membership_number='MEM005'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            available_copies=1
        )
    
    def test_list_borrowings(self):
        """Test listing borrowings."""
        response = self.client.get('/api/v1/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
