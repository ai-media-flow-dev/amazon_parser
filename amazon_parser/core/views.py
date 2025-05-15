import logging

from multiprocessing import Process
import re
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .cache_utils import get_parsing_status
from .models import Book, BookSeries, Language
from .forms import BookForm
from .filters import BookFilter
from .tasks import parse_single_book, parse_all_books as parse_all_books_task

logger = logging.getLogger(__name__)

def book_list(request):
    book_filter = BookFilter(request.GET, queryset=Book.objects.all())
    
    books = book_filter.qs
    
    all_series = BookSeries.objects.values_list('title', flat=True).distinct()
    
    paginator = Paginator(books, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter': book_filter,
        'all_series': all_series,
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
            logger.error(f'An error occurred while editing a book', exc_info=form.errors)
            messages.error(request, 'An error occurred while editing a book')
            return render(request, 'core/edit_book.html', {'form': form, 'book': book})
    else:
        match = re.search(r'/dp/([A-Z0-9]+)', book.url)
        if match:
            book_id = match.group(1)
        else:
            book_id = None

        form = BookForm(
            instance=book,
            initial={
                'series_title': book.series.title if book.series else '',
                'book_id': book_id
            }
        )
    
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
