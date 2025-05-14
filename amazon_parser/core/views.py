import logging
from multiprocessing import Process
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q

from .cache_utils import get_parsing_status
from .models import Book, BookSeries, Language
from .forms import BookForm
from .tasks import parse_single_book, parse_all_books as parse_all_books_task

logger = logging.getLogger(__name__)

def book_list(request):
    # Get filter parameters
    search_query = request.GET.get('search', '')
    series_filter = request.GET.get('series', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', '-created_at')
    language_filter = request.GET.get('language', '')
    
    # Start with all books
    books = Book.objects.all()
    
    # Apply filters
    if search_query:
        books = books.filter(Q(name__icontains=search_query) | Q(series__title__icontains=search_query))
    
    if series_filter:
        books = books.filter(series__title=series_filter)
    
    if language_filter:
        books = books.filter(language=language_filter)
    
    if date_from:
        books = books.filter(created_at__gte=date_from)
    
    if date_to:
        books = books.filter(created_at__lte=date_to)
    
    # Apply sorting
    valid_sort_fields = ['created_at', '-created_at', 'name', '-name', 'series__title', '-series__title']
    if sort_by in valid_sort_fields:
        books = books.order_by(sort_by)
    else:
        books = books.order_by('-created_at')
    
    # Get all series for the filter dropdown
    all_series = BookSeries.objects.values_list('title', flat=True).distinct()
    
    paginator = Paginator(books, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'series_filter': series_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'all_series': all_series,
        'language_filter': language_filter,
        'language_choices': Language.choices,
        'parsing_in_progress': get_parsing_status(),
    }
    
    return render(request, 'core/book_list.html', context)

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    return render(request, 'core/book_detail.html', {
        'book': book,
    })

def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Book added successfully!')
                return redirect('book_list')
            except IntegrityError as ex:
                logger.error(f'An error occurred while adding a book', exc_info=ex)
                form.add_error('book_id', 'Book with such url already exists')
                return render(request, 'core/add_book.html', {'form': form})
    else:
        form = BookForm()
    
    return render(request, 'core/add_book.html', {'form': form})

def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_list')
    else:
        form = BookForm(instance=book, initial={'series_title': book.series.title if book.series else ''})
    
    return render(request, 'core/edit_book.html', {'form': form, 'book': book})

@require_POST
def parse_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    # Call the parse function
    parse_single_book(book.pk)
    
    messages.info(request, f'Parsing started for book: {book.name}')
    return redirect('book_detail', pk=book.pk)

@require_POST
def parse_all_books(request):
    if get_parsing_status():
        messages.info(request, 'Parsing already in progress')
        return redirect('book_list')
    
    books = Book.objects.all()
    process = Process(target=parse_all_books_task, daemon=True)
    process.start()
    messages.success(request, f'Parsing started for all {books.count()} books')
    return redirect('book_list')

@require_POST
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, f'Book "{book.name}" was successfully deleted.')
    return redirect('book_list')
