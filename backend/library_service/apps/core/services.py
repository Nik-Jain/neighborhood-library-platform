"""
Service layer for borrowing operations.

This module encapsulates the business logic for borrowing and returning books,
ensuring transactional consistency and concurrency safety.
"""
from typing import Optional, Tuple
from uuid import UUID
from django.db import transaction, IntegrityError
from django.db.models import F
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import logging

from .models import Member, Book, Borrowing, Fine
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

logger = logging.getLogger(__name__)


class BorrowingService:
    """
    Service class for handling borrowing operations.
    
    Provides transactional and concurrency-safe methods for:
    - Creating borrowings (borrowing books)
    - Returning borrowings
    - Fine calculation and creation
    """
    
    FINE_RATE_PER_DAY = Decimal('1.00')  # $1.00 per day overdue
    DEFAULT_BORROW_PERIOD_DAYS = 14  # Default 2-week borrowing period
    
    @classmethod
    @transaction.atomic
    def create_borrowing(
        cls,
        member_id: UUID,
        book_id: UUID,
        due_date: Optional[date] = None,
        notes: Optional[str] = None
    ) -> Borrowing:
        """
        Create a new borrowing record (member borrows a book).
        
        This method is wrapped in a transaction to ensure atomicity.
        Uses select_for_update to prevent race conditions.
        
        Args:
            member_id: UUID of the member
            book_id: UUID of the book
            due_date: Optional custom due date
            notes: Optional notes for the borrowing
            
        Returns:
            Borrowing: The created borrowing instance
            
        Raises:
            MemberNotFoundException: If member does not exist
            BookNotFoundException: If book does not exist
            MemberNotActiveException: If member is not active
            BookNotAvailableException: If book has no available copies
            BookAlreadyBorrowedException: If member already has this book
            ConcurrencyException: If concurrent modification detected
        """
        # Lock rows to prevent concurrent modifications
        try:
            member = Member.objects.select_for_update().get(id=member_id)
        except Member.DoesNotExist:
            raise MemberNotFoundException(
                f"Member with ID {member_id} not found."
            )
        
        if member.membership_status != 'active':
            raise MemberNotActiveException(
                f"Member {member.full_name} is {member.membership_status}."
            )
        
        # Lock book first to prevent concurrent access issues
        try:
            book = Book.objects.select_for_update().get(id=book_id)
        except Book.DoesNotExist:
            raise BookNotFoundException(
                f"Book with ID {book_id} not found."
            )
        
        # Check if book has available copies (now under lock)
        if book.available_copies <= 0:
            raise BookNotAvailableException(
                f"'{book.title}' has no available copies."
            )
        
        # Note: We don't manually check for duplicate borrowings here.
        # The database constraint 'unique_active_borrowing_per_member_book'
        # will catch duplicates and we'll handle the IntegrityError below.
        
        # Decrement available copies using F() expression to avoid race conditions
        updated_count = Book.objects.filter(
            id=book_id,
            available_copies__gt=0
        ).update(available_copies=F('available_copies') - 1)
        
        if updated_count == 0:
            # Another transaction took the last copy
            raise ConcurrencyException(
                "Book became unavailable during checkout. Please retry."
            )
        
        # Refresh book instance to get updated values
        book.refresh_from_db()
        
        # Create borrowing record
        # The DB constraint will prevent duplicate active borrowings
        try:
            borrowing = Borrowing.objects.create(
                member=member,
                book=book,
                due_date=due_date,
                notes=notes
            )
        except IntegrityError as e:
            # Check if it's the duplicate borrowing constraint
            if 'unique_active_borrowing_per_member_book' in str(e):
                raise BookAlreadyBorrowedException(
                    f"Member already has '{book.title}' borrowed."
                )
            # Re-raise if it's a different integrity error
            raise
        
        logger.info(
            f"Borrowing created: Member ID {member.id} borrowed Book ID {book.id} "
            f"(Borrowing ID: {borrowing.id}, Available: {book.available_copies})"
        )
        
        return borrowing
    
    @classmethod
    @transaction.atomic
    def return_borrowing(cls, borrowing_id: UUID) -> Tuple[Borrowing, Optional[Fine]]:
        """
        Process the return of a borrowed book.
        
        This method is wrapped in a transaction to ensure atomicity.
        It handles:
        - Marking borrowing as returned
        - Incrementing available copies
        - Creating fines for overdue returns
        
        Args:
            borrowing_id: UUID of the borrowing record
            
        Returns:
            tuple: (Borrowing instance, Fine instance or None)
            
        Raises:
            BorrowingNotFoundException: If borrowing does not exist
            BorrowingAlreadyReturnedException: If already returned
        """
        # Lock borrowing and related book for update
        try:
            borrowing = Borrowing.objects.select_for_update().select_related(
                'member', 'book'
            ).get(id=borrowing_id)
        except Borrowing.DoesNotExist:
            raise BorrowingNotFoundException(
                f"Borrowing with ID {borrowing_id} not found."
            )
        
        if borrowing.returned_at:
            raise BorrowingAlreadyReturnedException(
                f"Book '{borrowing.book.title}' has already been returned."
            )
        
        # Lock the book row
        book = Book.objects.select_for_update().get(id=borrowing.book.id)
        
        # Calculate overdue days
        returned_at = timezone.now()
        days_overdue = max((returned_at.date() - borrowing.due_date).days, 0)
        
        # Mark borrowing as returned
        borrowing.returned_at = returned_at
        borrowing.save(update_fields=['returned_at'])
        
        # Increment available copies using F() expression, but ensure it doesn't exceed total_copies
        # Use a filter condition to prevent violating the check constraint
        updated_count = Book.objects.filter(
            id=book.id,
            available_copies__lt=F('total_copies')  # Only increment if available < total
        ).update(
            available_copies=F('available_copies') + 1
        )
        
        if updated_count == 0:
            # This shouldn't happen in normal circumstances - it means available_copies == total_copies
            # which would indicate a data consistency issue
            logger.warning(
                f"Book {book.id} already has available_copies == total_copies. "
                f"Skipping increment. Book: {book.title}, Available: {book.available_copies}, Total: {book.total_copies}"
            )
        
        # Refresh to get updated values
        book.refresh_from_db()
        
        # Create fine if overdue
        fine = None
        if days_overdue > 0:
            fine_amount = days_overdue * cls.FINE_RATE_PER_DAY
            try:
                fine, created = Fine.objects.get_or_create(
                    borrowing=borrowing,
                    defaults={
                        'amount': fine_amount,
                        'reason': f"Overdue by {days_overdue} day{'s' if days_overdue != 1 else ''}"
                    }
                )
            except IntegrityError:
                # Fine already exists, fetch it
                fine = Fine.objects.get(borrowing=borrowing)
                created = False
            
            if created:
                logger.warning(
                    f"Fine created: Member ID {borrowing.member.id} returned "
                    f"Book ID {borrowing.book.id} {days_overdue} days late "
                    f"(Amount: ${fine_amount})"
                )
        
        logger.info(
            f"Borrowing returned: Borrowing ID {borrowing.id} "
            f"(Member ID: {borrowing.member.id}, Book ID: {borrowing.book.id}, "
            f"Available: {book.available_copies}, Fine: ${fine.amount if fine else 0})"
        )
        
        return borrowing, fine
    
    @classmethod
    def calculate_fine_amount(cls, days_overdue: int) -> Decimal:
        """
        Calculate fine amount for given overdue days.
        
        Args:
            days_overdue: Number of days overdue
            
        Returns:
            Decimal: Fine amount
        """
        if days_overdue <= 0:
            return Decimal('0.00')
        return days_overdue * cls.FINE_RATE_PER_DAY
