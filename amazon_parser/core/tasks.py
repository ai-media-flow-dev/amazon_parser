"""
Tasks for asynchronous processing of book parsing
"""
from datetime import datetime
from .models import Book
from .utils import AmazonKDPParser

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
        print(f"Error parsing book {book_id}: {str(e)}")
        book.parse_status = 'error'
        book.save()
        return False

def parse_all_books():
    """
    Parse all books in the database
    """
    books = Book.objects.all()
    
    for book in books:
        parse_single_book(book.id)
    
    return True 