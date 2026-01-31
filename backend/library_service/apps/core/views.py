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

logger = logging.getLogger(__name__)


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing library members.
    
    Provides CRUD operations and additional actions for member management.
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
    
    @action(detail=True, methods=['get'])
    def borrowing_history(self, request, pk=None):
        """
        Get the borrowing history of a member.
        """
        member = self.get_object()
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
        """
        member = self.get_object()
        borrowings = member.get_active_borrowings()
        
        serializer = BorrowingListSerializer(borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def overdue_borrowings(self, request, pk=None):
        """
        Get overdue borrowings for a member.
        """
        member = self.get_object()
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
    """
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BorrowingFilterSet
    ordering_fields = ['borrowed_at', 'due_date', 'created_at']
    ordering = ['-borrowed_at']
    
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
        """
        overdue_borrowings = Borrowing.objects.filter(
            returned_at__isnull=True,
            due_date__lt=timezone.now().date()
        ).order_by('due_date')
        
        page = self.paginate_queryset(overdue_borrowings)
        if page is not None:
            serializer = BorrowingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowingListSerializer(overdue_borrowings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active borrowings.
        """
        active_borrowings = Borrowing.objects.filter(
            returned_at__isnull=True
        ).order_by('-borrowed_at')
        
        page = self.paginate_queryset(active_borrowings)
        if page is not None:
            serializer = BorrowingListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = BorrowingListSerializer(active_borrowings, many=True)
        return Response(serializer.data)


class FineViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing fines.
    """
    queryset = Fine.objects.all()
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_paid']
    ordering_fields = ['amount', 'created_at']
    ordering = ['-created_at']
    
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
        """
        unpaid_fines = Fine.objects.filter(is_paid=False).order_by('-created_at')
        
        page = self.paginate_queryset(unpaid_fines)
        if page is not None:
            serializer = FineSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = FineSerializer(unpaid_fines, many=True)
        return Response(serializer.data)
