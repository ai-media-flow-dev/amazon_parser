from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:pk>/parse/', views.parse_book, name='parse_book'),
    path('books/parse-all/', views.parse_all_books, name='parse_all_books'),
] 