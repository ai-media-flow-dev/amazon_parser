from django.db import models

# Create your models here.

class Status(models.TextChoices):
    NOT_PARSED = 'not parsed'
    IN_PROGRESS = 'in progress'
    COMPLETED = 'completed'
    ERROR = 'error'

class Language(models.TextChoices):
    ENGLISH = 'en'
    GERMAN = 'de'
    FRENCH = 'fr'
    ITALIAN = 'it'
    SPANISH = 'es'
    PORTUGUESE = 'pt'
    MEXICAN = 'mx'
    DUTCH = 'nl'
    RUSSIAN = 'ru'
    JAPANESE = 'ja'


class BookSeries(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return str(self.title)


class Book(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(null=False, blank=False, unique=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=255, null=False, blank=False, choices=Language.choices)
    
    series = models.ForeignKey(BookSeries, on_delete=models.CASCADE, related_name='books', null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    reviews_count = models.IntegerField(null=True, blank=True)
    best_seller_ranks = models.JSONField(null=True, blank=True)
    popular_reviews = models.JSONField(null=True, blank=True)
    parse_status = models.CharField(max_length=255, null=True, blank=True, choices=Status.choices)
    parsed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self) -> str:
        return str(self.name)
        
