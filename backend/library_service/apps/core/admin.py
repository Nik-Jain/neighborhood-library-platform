"""
Admin configuration for the core library service.
"""
from django.contrib import admin
from .models import Member, Book, Borrowing, Fine


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'membership_status', 'join_date')
    list_filter = ('membership_status', 'join_date')
    search_fields = ('first_name', 'last_name', 'email', 'membership_number')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address',),
            'classes': ('collapse',)
        }),
        ('Membership', {
            'fields': ('membership_number', 'membership_status', 'join_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'total_copies', 'available_copies', 'condition')
    list_filter = ('condition', 'language', 'publication_year')
    search_fields = ('title', 'author', 'isbn', 'publisher')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'title', 'author', 'isbn')
        }),
        ('Publication Details', {
            'fields': ('publisher', 'publication_year', 'language')
        }),
        ('Copies', {
            'fields': ('total_copies', 'available_copies')
        }),
        ('Additional Information', {
            'fields': ('description', 'condition'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_member_name', 'get_book_title', 'borrowed_at', 'due_date', 'returned_at', 'status')
    list_filter = ('borrowed_at', 'due_date', 'returned_at')
    search_fields = ('member__first_name', 'member__last_name', 'book__title')
    readonly_fields = ('id', 'borrowed_at', 'created_at', 'updated_at', 'status', 'is_overdue')
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('id', 'member', 'book', 'borrowed_at', 'due_date', 'returned_at')
        }),
        ('Status', {
            'fields': ('status', 'is_overdue')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return obj.member.full_name
    get_member_name.short_description = 'Member'
    
    def get_book_title(self, obj):
        return obj.book.title
    get_book_title.short_description = 'Book'
    
    def status(self, obj):
        return obj.status.upper()
    status.short_description = 'Status'


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_member_name', 'get_book_title', 'amount', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('borrowing__member__first_name', 'borrowing__member__last_name', 'borrowing__book__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Fine Details', {
            'fields': ('id', 'borrowing', 'amount', 'reason')
        }),
        ('Payment Status', {
            'fields': ('is_paid', 'paid_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_member_name(self, obj):
        return obj.borrowing.member.full_name
    get_member_name.short_description = 'Member'
    
    def get_book_title(self, obj):
        return obj.borrowing.book.title
    get_book_title.short_description = 'Book'
