"""
Serializers for the core library service application.
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Member, Book, Borrowing, Fine


class MemberSerializer(serializers.ModelSerializer):
    """
    Serializer for the Member model.
    """
    full_name = serializers.CharField(read_only=True)
    active_borrowings_count = serializers.SerializerMethodField()
    overdue_borrowings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'address', 'membership_number', 'membership_status', 'join_date',
            'created_at', 'updated_at', 'active_borrowings_count',
            'overdue_borrowings_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'membership_number': {'required': False, 'allow_blank': True},
        }
    
    def get_active_borrowings_count(self, obj):
        """Get count of active borrowings."""
        return obj.get_active_borrowings().count()
    
    def get_overdue_borrowings_count(self, obj):
        """Get count of overdue borrowings."""
        return obj.get_overdue_borrowings().count()
    
    def validate_email(self, value):
        """Validate email is unique."""
        if self.instance and self.instance.email == value:
            return value
        if Member.objects.filter(email=value).exists():
            raise serializers.ValidationError("A member with this email already exists.")
        return value

    def create(self, validated_data):
        """Create a member and auto-assign membership number when omitted."""
        membership_number = validated_data.get('membership_number')
        if not membership_number:
            import uuid
            validated_data['membership_number'] = f"LIB-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)


class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model.
    """
    is_available = serializers.BooleanField(read_only=True)
    borrowing_count = serializers.SerializerMethodField()
    active_borrowings_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'publisher', 'publication_year',
            'description', 'total_copies', 'available_copies', 'condition',
            'language', 'is_available', 'borrowing_count', 'active_borrowings_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_borrowing_count(self, obj):
        """Get total borrowing count for this book."""
        return obj.get_borrowing_count()
    
    def get_active_borrowings_count(self, obj):
        """Get active borrowings count for this book."""
        return obj.get_active_borrowings_count()
    
    def validate_total_copies(self, value):
        """Ensure total copies is at least 1."""
        if value < 1:
            raise serializers.ValidationError("Total copies must be at least 1.")
        return value
    
    def validate(self, data):
        """Validate available_copies doesn't exceed total_copies."""
        total_copies = data.get('total_copies', self.instance.total_copies if self.instance else 1)
        available_copies = data.get('available_copies', self.instance.available_copies if self.instance else 1)
        
        if available_copies > total_copies:
            raise serializers.ValidationError(
                "Available copies cannot exceed total copies."
            )
        return data


class FineSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for fine details attached to a borrowing.
    """

    class Meta:
        model = Fine
        fields = ['id', 'amount', 'reason', 'is_paid', 'paid_at']


class BorrowingListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing borrowings.
    """
    member_name = serializers.CharField(source='member.full_name', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    fine = FineSummarySerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Borrowing
        fields = [
            'id', 'member', 'member_name', 'book', 'book_title',
            'borrowed_at', 'due_date', 'returned_at', 'status',
            'is_overdue', 'days_until_due', 'days_overdue', 'fine'
        ]
        read_only_fields = [
            'id', 'borrowed_at', 'created_at', 'updated_at',
            'status', 'is_overdue', 'days_until_due', 'days_overdue'
        ]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for borrowing operations.
    """
    member = MemberSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    member_id = serializers.UUIDField(write_only=True)
    book_id = serializers.UUIDField(write_only=True)
    status = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_due = serializers.IntegerField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Borrowing
        fields = [
            'id', 'member', 'member_id', 'book', 'book_id',
            'borrowed_at', 'due_date', 'returned_at', 'notes',
            'status', 'is_overdue', 'days_until_due', 'days_overdue',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'borrowed_at', 'created_at', 'updated_at',
            'status', 'is_overdue', 'days_until_due', 'days_overdue'
        ]
        extra_kwargs = {
            'due_date': {'required': False},
            'notes': {'required': False},
        }
    
    def validate(self, data):
        """Validate borrowing operation."""
        member_id = data.get('member_id')
        book_id = data.get('book_id')
        
        # Validate member exists and is active
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            raise serializers.ValidationError("Member not found.")
        
        if member.membership_status != 'active':
            raise serializers.ValidationError("Member is not active.")
        
        # Validate book exists and has available copies
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError("Book not found.")
        
        if book.available_copies <= 0:
            raise serializers.ValidationError("Book is not available.")
        
        # Check if member already has this book borrowed
        if Borrowing.objects.filter(
            member=member,
            book=book,
            returned_at__isnull=True
        ).exists():
            raise serializers.ValidationError("Member already has this book borrowed.")
        
        data['member'] = member
        data['book'] = book
        
        return data


class FineSerializer(serializers.ModelSerializer):
    """
    Serializer for the Fine model.
    """
    borrowing_detail = BorrowingListSerializer(source='borrowing', read_only=True)
    
    class Meta:
        model = Fine
        fields = [
            'id', 'borrowing', 'borrowing_detail', 'amount', 'reason',
            'is_paid', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
