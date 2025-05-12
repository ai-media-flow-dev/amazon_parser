from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'series', 'created_at')
    search_fields = ('name', 'series')
