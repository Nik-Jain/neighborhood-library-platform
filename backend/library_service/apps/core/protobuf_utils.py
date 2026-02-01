"""
Protobuf serialization utilities for converting between Django models and protobuf messages.
"""
from decimal import Decimal
from django.utils import timezone
from datetime import date, datetime


class ProtobufSerializer:
    """Helper class to convert Django model instances to protobuf-compatible dicts."""
    
    @staticmethod
    def serialize_member(member, protobuf_dict):
        """Convert Member model to protobuf-compatible dict."""
        return {
            'id': str(member.id),
            'first_name': member.first_name,
            'last_name': member.last_name,
            'full_name': member.full_name,
            'email': member.email,
            'phone': member.phone or '',
            'address': member.address or '',
            'membership_number': member.membership_number,
            'membership_status': member.membership_status,
            'join_date': member.join_date.isoformat() if member.join_date else '',
            'created_at': member.created_at.isoformat() if member.created_at else '',
            'updated_at': member.updated_at.isoformat() if member.updated_at else '',
            'active_borrowings_count': protobuf_dict.get('active_borrowings_count', 0),
            'overdue_borrowings_count': protobuf_dict.get('overdue_borrowings_count', 0),
        }
    
    @staticmethod
    def serialize_book(book, protobuf_dict):
        """Convert Book model to protobuf-compatible dict."""
        return {
            'id': str(book.id),
            'isbn': book.isbn or '',
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher or '',
            'publication_year': book.publication_year or 0,
            'description': book.description or '',
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'condition': book.condition,
            'language': book.language,
            'is_available': book.is_available,
            'borrowing_count': protobuf_dict.get('borrowing_count', 0),
            'active_borrowings_count': protobuf_dict.get('active_borrowings_count', 0),
            'created_at': book.created_at.isoformat() if book.created_at else '',
            'updated_at': book.updated_at.isoformat() if book.updated_at else '',
        }
    
    @staticmethod
    def serialize_borrowing(borrowing, protobuf_dict):
        """Convert Borrowing model to protobuf-compatible dict."""
        return {
            'id': str(borrowing.id),
            'member': protobuf_dict.get('member', str(borrowing.member.id)),
            'member_id': protobuf_dict.get('member_id', str(borrowing.member.id)),
            'member_name': protobuf_dict.get('member_name', borrowing.member.full_name),
            'book': protobuf_dict.get('book', str(borrowing.book.id)),
            'book_id': protobuf_dict.get('book_id', str(borrowing.book.id)),
            'book_title': protobuf_dict.get('book_title', borrowing.book.title),
            'borrowed_at': borrowing.borrowed_at.isoformat() if borrowing.borrowed_at else '',
            'due_date': borrowing.due_date.isoformat() if borrowing.due_date else '',
            'returned_at': borrowing.returned_at.isoformat() if borrowing.returned_at else '',
            'status': borrowing.status,
            'days_until_due': borrowing.days_until_due or 0,
            'days_overdue': borrowing.days_overdue or 0,
            'is_overdue': borrowing.is_overdue,
            'notes': borrowing.notes or '',
            'created_at': borrowing.created_at.isoformat() if borrowing.created_at else '',
            'updated_at': borrowing.updated_at.isoformat() if borrowing.updated_at else '',
        }
    
    @staticmethod
    def serialize_fine(fine, protobuf_dict):
        """Convert Fine model to protobuf-compatible dict."""
        return {
            'id': str(fine.id),
            'borrowing_id': protobuf_dict.get('borrowing_id', str(fine.borrowing.id)),
            'member_id': protobuf_dict.get('member_id', str(fine.borrowing.member.id)),
            'member_name': protobuf_dict.get('member_name', fine.borrowing.member.full_name),
            'book_id': protobuf_dict.get('book_id', str(fine.borrowing.book.id)),
            'book_title': protobuf_dict.get('book_title', fine.borrowing.book.title),
            'amount': str(fine.amount),
            'reason': fine.reason,
            'is_paid': fine.is_paid,
            'paid_at': fine.paid_at.isoformat() if fine.paid_at else '',
            'created_at': fine.created_at.isoformat() if fine.created_at else '',
            'updated_at': fine.updated_at.isoformat() if fine.updated_at else '',
        }
    
    @staticmethod
    def serialize_value(value):
        """Convert various Python types to protobuf-compatible values."""
        if value is None:
            return ''
        elif isinstance(value, Decimal):
            return str(value)
        elif isinstance(value, (date, datetime)):
            return value.isoformat()
        elif isinstance(value, bool):
            return value
        elif isinstance(value, (int, float)):
            return value
        else:
            return str(value)
