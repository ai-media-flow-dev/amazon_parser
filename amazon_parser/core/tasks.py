"""
Tasks for asynchronous processing of book parsing
"""
from datetime import datetime
import logging

from .cache_utils import set_parsing_status
from .models import Book
from .utils import AmazonKDPParser

logger = logging.getLogger(__name__)

def parse_single_book(book_id):
    """
    Parse a single book by its ID
    
    Args:
        book_id (int): The ID of the book to parse
    """
    book = Book.objects.get(id=book_id)

    try:
        # Call your parsing function
        parser = AmazonKDPParser()
        parsed_data = parser.parse_amazon_book(book.url)
        book.rating = parsed_data.rating
        book.reviews_count = parsed_data.reviews_count
        book.best_seller_ranks = parsed_data.best_sellers_ranks
        book.popular_reviews = parsed_data.reviews
        book.parse_status = 'completed'
        book.parsed_at = datetime.now()
        book.save()
        return True
    except Exception as e:
        logger.error(f"Error parsing book {book_id}", exc_info=e)
        book.parse_status = 'error'
        book.save()
        return False

def parse_all_books():
    """
    Parse all books in separate process
    """
    try:
        from django import db
        db.connection.close()
        set_parsing_status(True)
        books = Book.objects.all()
        for book in books:
            parse_single_book(book.id)
    finally:
        set_parsing_status(False)
