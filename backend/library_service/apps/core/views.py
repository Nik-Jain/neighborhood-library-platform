"""
Views for the core library service application.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Member, Book, Borrowing, Fine
from .serializers import (
    MemberSerializer,
    BookSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    FineSerializer
)
from .filters import BorrowingFilterSet, BookFilterSet, MemberFilterSet
from .pagination import StandardResultsSetPagination
from .permissions import IsAdmin, IsAdminOrLibrarian, IsMember

logger = logging.getLogger(__name__)


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing library members.
    
    Provides CRUD operations and additional actions for member management.
    - List/Read: Any authenticated user
    - Create/Update/Delete: ADMIN or LIBRARIAN only
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MemberFilterSet
    search_fields = ['first_name', 'last_name', 'email', 'membership_number']
    ordering_fields = ['first_name', 'last_name', 'join_date', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Apply different permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'suspend', 'activate']:
            return [IsAdminOrLibrarian()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter members: MEMBERs see only their own profile; ADMIN/LIBRARIAN see all."""
        queryset = super().get_queryset()
        user = self.request.user

        # Check if user is ADMIN or LIBRARIAN
        if user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            return queryset

        # MEMBERs see only their own profile
        try:
            member = Member.objects.get(email=user.username)
            return queryset.filter(id=member.id)
        except Member.DoesNotExist:
            return queryset.none()
    
    @action(detail=True, methods=['get'])
    def borrowing_history(self, request, pk=None):
        """
        Get the borrowing history of a member.
        Members can only view their own history; ADMIN/LIBRARIAN can view any.
        """
        member = self.get_object()
        user = self.request.user
        
        # Check if member user is trying to view someone else's history
        if not user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            try:
                user_member = Member.objects.get(email=user.username)
                if user_member.id != member.id:
                    return Response(
                        {'error': 'You can only view your own borrowing history.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Member.DoesNotExist:
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        borrowings = member.borrowing_set.all().order_by('-borrowed_at')
        
        page = self.paginate_queryset(borrowings)
        if page is not None:
            serializer = BorrowingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def active_borrowings(self, request, pk=None):
        """
        Get currently active borrowings for a member.
        Members can only view their own; ADMIN/LIBRARIAN can view any.
        """
        member = self.get_object()
        user = self.request.user
        
        # Check if member user is trying to view someone else's borrowings
        if not user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            try:
                user_member = Member.objects.get(email=user.username)
                if user_member.id != member.id:
                    return Response(
                        {'error': 'You can only view your own active borrowings.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Member.DoesNotExist:
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        borrowings = member.get_active_borrowings()
        
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def overdue_borrowings(self, request, pk=None):
        """
        Get overdue borrowings for a member.
        Members can only view their own; ADMIN/LIBRARIAN can view any.
        """
        member = self.get_object()
        user = self.request.user
        
        # Check if member user is trying to view someone else's overdue borrowings
        if not user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            try:
                user_member = Member.objects.get(email=user.username)
                if user_member.id != member.id:
                    return Response(
                        {'error': 'You can only view your own overdue borrowings.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Member.DoesNotExist:
                return Response(
                    {'error': 'Unauthorized'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        borrowings = member.get_overdue_borrowings()
        
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        """
        Suspend a member's account.
        """
        member = self.get_object()
        member.membership_status = 'suspended'
        member.save()
        
        serializer = self.get_serializer(member)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activate a member's account.
        """
        member = self.get_object()
        member.membership_status = 'active'
        member.save()
        
        serializer = self.get_serializer(member)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing library books.
    
    Provides CRUD operations and additional actions for book management.
    - List/Read: Any authenticated user
    - Create/Update/Delete: ADMIN or LIBRARIAN only
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BookFilterSet
    search_fields = ['title', 'author', 'isbn', 'publisher']
    ordering_fields = ['title', 'author', 'publication_year', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Apply different permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'increase_copies']:
            return [IsAdminOrLibrarian()]
        return [IsAuthenticated()]
    
    @action(detail=True, methods=['get'])
    def borrowing_history(self, request, pk=None):
        """
        Get the borrowing history of a book.
        """
        book = self.get_object()
        borrowings = book.borrowing_set.all().order_by('-borrowed_at')
        
        page = self.paginate_queryset(borrowings)
        if page is not None:
            serializer = BorrowingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increase_copies(self, request, pk=None):
        """
        Increase the total number of copies of a book.
        """
        book = self.get_object()
        quantity = request.data.get('quantity', 1)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return Response(
                    {'error': 'Quantity must be positive.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        book.total_copies += quantity
        book.available_copies += quantity
        book.save()
        
        serializer = self.get_serializer(book)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def available_count(self, request, pk=None):
        """
        Get the available count of a book.
        """
        book = self.get_object()
        return Response({
            'book_id': str(book.id),
            'title': book.title,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'is_available': book.is_available
        })


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing borrowing operations.
    
    Handles borrowing, returning, and tracking of books.
    - List/Read: ADMIN/LIBRARIAN see all; MEMBER sees only their own
    - Create/Update/Delete: ADMIN or LIBRARIAN only
    - return_book: ADMIN or LIBRARIAN only
    """
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BorrowingFilterSet
    ordering_fields = ['borrowed_at', 'due_date', 'created_at']
    ordering = ['-borrowed_at']

    def get_permissions(self):
        """Apply different permissions based on action."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'return_book']:
            return [IsAdminOrLibrarian()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """Filter borrowings: MEMBERs see only their own; ADMIN/LIBRARIAN see all."""
        queryset = super().get_queryset()
        user = self.request.user

        # Check if user is ADMIN or LIBRARIAN
        if user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            return queryset

        # MEMBERs see only their own borrowings
        # Find the Member record linked to this user
        try:
            from .models import Member
            member = Member.objects.get(email=user.username)
            return queryset.filter(member=member)
        except Member.DoesNotExist:
            return queryset.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BorrowingListSerializer
        return BorrowingDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new borrowing record (member borrows a book).
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            member = serializer.validated_data.pop('member')
            book = serializer.validated_data.pop('book')
            
            # Update book availability
            book.available_copies -= 1
            book.save()
            
            # Create borrowing record
            borrowing = Borrowing.objects.create(
                member=member,
                book=book,
                **serializer.validated_data
            )
            
            logger.info(
                f"Book borrowed: {member.full_name} borrowed {book.title}"
            )
            
            output_serializer = BorrowingDetailSerializer(borrowing)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error creating borrowing: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """
        Record the return of a borrowed book.
        """
        borrowing = self.get_object()
        
        if borrowing.returned_at:
            return Response(
                {'error': 'This book has already been returned.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark as returned
        borrowing.returned_at = timezone.now()
        borrowing.save()
        
        # Update book availability
        borrowing.book.available_copies += 1
        borrowing.book.save()
        
        # Check for overdue and create fine if needed
        if borrowing.is_overdue:
            days_overdue = borrowing.days_overdue
            fine_amount = days_overdue * 0.50  # $0.50 per day
            
            Fine.objects.create(
                borrowing=borrowing,
                amount=fine_amount,
                reason=f"Overdue by {days_overdue} days"
            )
            
            logger.warning(
                f"Fine created: {borrowing.member.full_name} "
                f"returned {borrowing.book.title} {days_overdue} days late"
            )
        
        logger.info(
            f"Book returned: {borrowing.member.full_name} returned {borrowing.book.title}"
        )
        
        serializer = BorrowingDetailSerializer(borrowing)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """
        Get all overdue borrowings.
        Respects role-based filtering: MEMBERs see only their own; ADMIN/LIBRARIAN see all.
        """
        # Start with the role-filtered queryset from get_queryset()
        queryset = self.get_queryset().filter(
            returned_at__isnull=True,
            due_date__lt=timezone.now().date()
        ).order_by('due_date')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = BorrowingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowingListSerializer(queryset, many=True)
        return Response(serializer.data)
    
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


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing fines.
    - List/Read: Any authenticated user
    - mark_as_paid: ADMIN or LIBRARIAN only
    """
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_paid']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Apply IsAdminOrLibrarian permission for mark_as_paid action."""
        if self.action == 'mark_as_paid':
            return [IsAdminOrLibrarian()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter fines: MEMBERs see only their own; ADMIN/LIBRARIAN see all."""
        queryset = super().get_queryset()
        user = self.request.user

        # Check if user is ADMIN or LIBRARIAN
        if user.groups.filter(name__in=['ADMIN', 'LIBRARIAN']).exists():
            return queryset

        # MEMBERs see only their own fines
        try:
            from .models import Member
            member = Member.objects.get(email=user.username)
            # Filter fines by borrowing's member
            return queryset.filter(borrowing__member=member)
        except Member.DoesNotExist:
            return queryset.none()
    
    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """
        Mark a fine as paid.
        """
        fine = self.get_object()
        fine.is_paid = True
        fine.paid_at = timezone.now()
        fine.save()
        
        logger.info(f"Fine marked as paid: {fine.id}")
        
        serializer = self.get_serializer(fine)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unpaid(self, request):
        """
        Get all unpaid fines.
        Respects role-based filtering: MEMBERs see only their own; ADMIN/LIBRARIAN see all.
        """
        # Start with the role-filtered queryset from get_queryset()
        queryset = self.get_queryset().filter(is_paid=False).order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = FineSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FineSerializer(queryset, many=True)
        return Response(serializer.data)
