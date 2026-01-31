"""
URL configuration for the core library service.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MemberViewSet,
    BookViewSet,
    BorrowingViewSet,
    FineViewSet
)

app_name = 'core'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'members', MemberViewSet, basename='member')
router.register(r'books', BookViewSet, basename='book')
router.register(r'borrowings', BorrowingViewSet, basename='borrowing')
router.register(r'fines', FineViewSet, basename='fine')

urlpatterns = [
    path('', include(router.urls)),
]
