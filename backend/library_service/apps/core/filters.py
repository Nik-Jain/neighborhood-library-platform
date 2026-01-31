"""
Filters for the core library service application.
"""
import django_filters
from .models import Member, Book, Borrowing


class MemberFilterSet(django_filters.FilterSet):
    """
    Filter set for Member model.
    """
    join_date_from = django_filters.DateFilter(
        field_name='join_date',
        lookup_expr='gte'
    )
    join_date_to = django_filters.DateFilter(
        field_name='join_date',
        lookup_expr='lte'
    )
    
    class Meta:
        model = Member
        fields = ['membership_status']


class BookFilterSet(django_filters.FilterSet):
    """
    Filter set for Book model.
    """
    publication_year_from = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='gte'
    )
    publication_year_to = django_filters.NumberFilter(
        field_name='publication_year',
        lookup_expr='lte'
    )
    is_available = django_filters.BooleanFilter(field_name='available_copies', method='filter_available')
    
    def filter_available(self, queryset, name, value):
        if value:
            return queryset.filter(available_copies__gt=0)
        return queryset.filter(available_copies=0)
    
    class Meta:
        model = Book
        fields = ['condition', 'language']


class BorrowingFilterSet(django_filters.FilterSet):
    """
    Filter set for Borrowing model.
    """
    borrowed_from = django_filters.DateFilter(
        field_name='borrowed_at',
        lookup_expr='gte'
    )
    borrowed_to = django_filters.DateFilter(
        field_name='borrowed_at',
        lookup_expr='lte'
    )
    due_date_from = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='gte'
    )
    due_date_to = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='lte'
    )
    is_active = django_filters.BooleanFilter(
        field_name='returned_at',
        method='filter_active'
    )
    
    def filter_active(self, queryset, name, value):
        if value:
            return queryset.filter(returned_at__isnull=True)
        return queryset.filter(returned_at__isnull=False)
    
    class Meta:
        model = Borrowing
        fields = ['member', 'book']
