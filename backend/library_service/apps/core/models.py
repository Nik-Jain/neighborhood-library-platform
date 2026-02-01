"""
Models for the core library service application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
import uuid


class TimestampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    created and modified timestamps.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Member(TimestampedModel):
    """
    Model representing a library member.
    """
    MEMBERSHIP_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_number = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255, blank=False, null=False, default='user123')
    membership_status = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default='active'
    )
    join_date = models.DateField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['membership_status']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Check if the provided password matches the stored hash."""
        return check_password(raw_password, self.password)
    
    def get_active_borrowings(self):
        """Get all currently active borrowings for this member."""
        return self.borrowing_set.filter(returned_at__isnull=True)
    
    def get_overdue_borrowings(self):
        """Get all overdue borrowings for this member."""
        return self.get_active_borrowings().filter(
            due_date__lt=timezone.now().date()
        )


class Book(TimestampedModel):
    """
    Model representing a book in the library.
    """
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1000), MaxValueValidator(2100)],
        null=True,
        blank=True
    )
    description = models.TextField(blank=True, null=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
        default='excellent'
    )
    language = models.CharField(max_length=50, default='English')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['isbn']),
        ]
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def is_available(self):
        """Check if the book has available copies."""
        return self.available_copies > 0
    
    def get_borrowing_count(self):
        """Get the number of times this book has been borrowed."""
        return self.borrowing_set.filter(returned_at__isnull=False).count()


class Borrowing(TimestampedModel):
    """
    Model representing a borrowing transaction between a member and a book.
    """
    BORROWING_STATUS_CHOICES = [
        ('active', 'Active'),
        ('overdue', 'Overdue'),
        ('returned', 'Returned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-borrowed_at']
        indexes = [
            models.Index(fields=['member', 'returned_at']),
            models.Index(fields=['book', 'returned_at']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.member.full_name} borrowed {self.book.title}"
    
    def save(self, *args, **kwargs):
        """Override save to set due_date if not provided."""
        if not self.due_date:
            # Default borrowing period is 14 days
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if the borrowing is overdue."""
        if self.returned_at:
            return False
        return timezone.now().date() > self.due_date
    
    @property
    def days_until_due(self):
        """Calculate days until due date."""
        if self.returned_at:
            return None
        return (self.due_date - timezone.now().date()).days
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (timezone.now().date() - self.due_date).days
    
    @property
    def status(self):
        """Get the current status of the borrowing."""
        if self.returned_at:
            return 'returned'
        if self.is_overdue:
            return 'overdue'
        return 'active'


class Fine(TimestampedModel):
    """
    Model representing fines for overdue books.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrowing = models.OneToOneField(Borrowing, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Fine for {self.borrowing.member.full_name} - ${self.amount}"
