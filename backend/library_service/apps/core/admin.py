"""
Admin configuration for the core library service.
"""
from django.contrib import admin, messages
from django import forms
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from django.template.response import TemplateResponse
from .models import Member, Book, Borrowing, Fine


class PasswordChangeForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput, label='New password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm new password')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'membership_status', 'join_date')
    list_filter = ('membership_status', 'join_date')
    search_fields = ('first_name', 'last_name', 'email', 'membership_number')
    readonly_fields = ('id', 'created_at', 'updated_at', 'join_date', 'password', 'password_change_link')

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
        ('Account', {
            'fields': ('password_change_link',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/password/',
                self.admin_site.admin_view(self.change_password),
                name='core_member_change_password',
            ),
        ]
        return custom_urls + urls

    def password_change_link(self, obj):
        if not obj.pk:
            return ''
        url = reverse('admin:core_member_change_password', args=[obj.pk])
        return format_html('<a class="button" href="{}">Change/Reset password</a>', url)
    password_change_link.short_description = 'Password'

    def change_password(self, request, object_id):
        member = get_object_or_404(Member, pk=object_id)
        if request.method == 'POST':
            form = PasswordChangeForm(request.POST)
            if form.is_valid():
                p1 = form.cleaned_data['password1']
                p2 = form.cleaned_data['password2']
                if p1 != p2:
                    messages.error(request, 'Passwords do not match.')
                else:
                    member.set_password(p1)
                    member.save(update_fields=['password'])
                    messages.success(request, 'Password updated successfully.')
                    return redirect(reverse('admin:core_member_change', args=[member.pk]))
        else:
            form = PasswordChangeForm()

        context = dict(
            self.admin_site.each_context(request),
            title=f'Change password: {member}',
            form=form,
            member=member,
            opts=self.model._meta,
        )
        return TemplateResponse(request, 'admin/core/member/change_password.html', context)


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
