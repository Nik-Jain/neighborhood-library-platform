"""
Integration tests for RBAC-protected API endpoints.
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

from library_service.apps.core.models import Member, Book, Borrowing, Fine, APIToken


class RBACIntegrationTestCase(TestCase):
    """Integration tests for RBAC on API endpoints."""

    def setUp(self):
        """Set up test data and clients."""
        # Create groups
        self.admin_group, _ = Group.objects.get_or_create(name='ADMIN')
        self.librarian_group, _ = Group.objects.get_or_create(name='LIBRARIAN')
        self.member_group, _ = Group.objects.get_or_create(name='MEMBER')
        
        # Create users
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='pass123'
        )
        self.admin_user.groups.add(self.admin_group)
        self.admin_token = APIToken.objects.create(user=self.admin_user)
        
        self.librarian_user = User.objects.create_user(
            username='librarian@test.com',
            email='librarian@test.com',
            password='pass123'
        )
        self.librarian_user.groups.add(self.librarian_group)
        self.librarian_token = APIToken.objects.create(user=self.librarian_user)
        
        self.member_user = User.objects.create_user(
            username='member@test.com',
            email='member@test.com',
            password='pass123'
        )
        self.member_user.groups.add(self.member_group)
        self.member_token = APIToken.objects.create(user=self.member_user)
        
        # Create corresponding Member records
        self.admin_member = Member.objects.create(
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            membership_number='ADMIN-001',
            membership_status='active'
        )
        
        self.librarian_member = Member.objects.create(
            first_name='Librarian',
            last_name='User',
            email='librarian@test.com',
            membership_number='LIB-001',
            membership_status='active'
        )
        
        self.member_record = Member.objects.create(
            first_name='Member',
            last_name='User',
            email='member@test.com',
            membership_number='MEM-001',
            membership_status='active'
        )
        
        # Create a sample book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            total_copies=5,
            available_copies=5
        )
        
        # Create API clients
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        self.librarian_client = APIClient()
        self.librarian_client.credentials(HTTP_AUTHORIZATION=f'Token {self.librarian_token.key}')
        
        self.member_client = APIClient()
        self.member_client.credentials(HTTP_AUTHORIZATION=f'Token {self.member_token.key}')
        
        self.anon_client = APIClient()

    def test_book_create_requires_admin_or_librarian(self):
        """Test book creation requires ADMIN or LIBRARIAN role."""
        book_data = {
            'title': 'New Book',
            'author': 'New Author',
            'total_copies': 3,
            'available_copies': 3
        }
        
        # Admin can create
        response = self.admin_client.post('/api/v1/books/', book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Librarian can create
        response = self.librarian_client.post('/api/v1/books/', book_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Member cannot create
        response = self.member_client.post('/api/v1/books/', book_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Anonymous cannot create
        response = self.anon_client.post('/api/v1/books/', book_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_book_update_requires_admin_or_librarian(self):
        """Test book update requires ADMIN or LIBRARIAN role."""
        update_data = {'title': 'Updated Title'}
        
        # Admin can update
        response = self.admin_client.patch(f'/api/v1/books/{self.book.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Librarian can update
        response = self.librarian_client.patch(f'/api/v1/books/{self.book.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Member cannot update
        response = self.member_client.patch(f'/api/v1/books/{self.book.id}/', update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_list_accessible_to_authenticated(self):
        """Test book list is accessible to all authenticated users."""
        # Admin can list
        response = self.admin_client.get('/api/v1/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Librarian can list
        response = self.librarian_client.get('/api/v1/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Member can list
        response = self.member_client.get('/api/v1/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Anonymous cannot list (if auth required)
        response = self.anon_client.get('/api/v1/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_member_create_requires_admin_or_librarian(self):
        """Test member creation requires ADMIN or LIBRARIAN role."""
        member_data = {
            'first_name': 'New',
            'last_name': 'Member',
            'email': 'newmember@test.com',
            'membership_number': 'MEM-999',
            'membership_status': 'active'
        }
        
        # Admin can create
        response = self.admin_client.post('/api/v1/members/', member_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Librarian can create
        member_data['email'] = 'newmember2@test.com'
        member_data['membership_number'] = 'MEM-998'
        response = self.librarian_client.post('/api/v1/members/', member_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Member cannot create
        member_data['email'] = 'newmember3@test.com'
        member_data['membership_number'] = 'MEM-997'
        response = self.member_client.post('/api/v1/members/', member_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_borrowing_create_requires_admin_or_librarian(self):
        """Test borrowing creation requires ADMIN or LIBRARIAN role."""
        # Ensure book has available copies
        self.book.available_copies = 3
        self.book.save()
        
        borrowing_data = {
            'member_id': str(self.member_record.id),
            'book_id': str(self.book.id)
        }
        
        # Admin can create
        response = self.admin_client.post('/api/v1/borrowings/', borrowing_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Admin create failed with: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Create another book for librarian test
        book2 = Book.objects.create(
            title='Test Book 2',
            author='Test Author',
            total_copies=5,
            available_copies=5
        )
        borrowing_data['book_id'] = str(book2.id)
        
        # Librarian can create
        response = self.librarian_client.post('/api/v1/borrowings/', borrowing_data, format='json')
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Librarian create failed with: {response.status_code}, {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Member cannot create
        book3 = Book.objects.create(
            title='Test Book 3',
            author='Test Author',
            total_copies=5,
            available_copies=5
        )
        borrowing_data['book_id'] = str(book3.id)
        response = self.member_client.post('/api/v1/borrowings/', borrowing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_sees_only_own_borrowings(self):
        """Test MEMBERs can only see their own borrowings."""
        # Create borrowings for different members
        borrowing1 = Borrowing.objects.create(
            member=self.member_record,
            book=self.book
        )
        
        other_member = Member.objects.create(
            first_name='Other',
            last_name='Member',
            email='other@test.com',
            membership_number='MEM-002',
            membership_status='active'
        )
        book2 = Book.objects.create(
            title='Test Book 2',
            author='Test Author',
            total_copies=5,
            available_copies=4
        )
        borrowing2 = Borrowing.objects.create(
            member=other_member,
            book=book2
        )
        
        # Member sees only their own
        response = self.member_client.get('/api/v1/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], str(borrowing1.id))
        
        # Admin sees all
        response = self.admin_client.get('/api/v1/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)
        
        # Librarian sees all
        response = self.librarian_client.get('/api/v1/borrowings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 2)

    def test_return_book_requires_admin_or_librarian(self):
        """Test return_book action requires ADMIN or LIBRARIAN role."""
        borrowing = Borrowing.objects.create(
            member=self.member_record,
            book=self.book
        )
        
        # Member cannot return
        response = self.member_client.post(f'/api/v1/borrowings/{borrowing.id}/return_book/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin can return
        response = self.admin_client.post(f'/api/v1/borrowings/{borrowing.id}/return_book/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create another borrowing for librarian test
        book2 = Book.objects.create(
            title='Test Book 2',
            author='Test Author',
            total_copies=5,
            available_copies=4
        )
        borrowing2 = Borrowing.objects.create(
            member=self.member_record,
            book=book2
        )
        
        # Librarian can return
        response = self.librarian_client.post(f'/api/v1/borrowings/{borrowing2.id}/return_book/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_mark_fine_as_paid_requires_admin_or_librarian(self):
        """Test mark_as_paid on fines requires ADMIN or LIBRARIAN role."""
        borrowing = Borrowing.objects.create(
            member=self.member_record,
            book=self.book
        )
        fine = Fine.objects.create(
            borrowing=borrowing,
            amount=Decimal('5.00'),
            reason='Test fine'
        )
        
        # Member cannot mark as paid
        response = self.member_client.post(f'/api/v1/fines/{fine.id}/mark_as_paid/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin can mark as paid
        response = self.admin_client.post(f'/api/v1/fines/{fine.id}/mark_as_paid/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Create another fine for librarian test
        book2 = Book.objects.create(
            title='Test Book 2',
            author='Test Author',
            total_copies=5,
            available_copies=5
        )
        borrowing2 = Borrowing.objects.create(
            member=self.member_record,
            book=book2
        )
        fine2 = Fine.objects.create(
            borrowing=borrowing2,
            amount=Decimal('3.00'),
            reason='Test fine 2'
        )
        
        # Librarian can mark as paid
        response = self.librarian_client.post(f'/api/v1/fines/{fine2.id}/mark_as_paid/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_suspend_activate_member_requires_admin_or_librarian(self):
        """Test member suspend/activate requires ADMIN or LIBRARIAN role."""
        # Member cannot suspend
        response = self.member_client.post(f'/api/v1/members/{self.member_record.id}/suspend/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin can suspend
        response = self.admin_client.post(f'/api/v1/members/{self.member_record.id}/suspend/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Librarian can activate
        response = self.librarian_client.post(f'/api/v1/members/{self.member_record.id}/activate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
