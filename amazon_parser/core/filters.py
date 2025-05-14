from django_filters import FilterSet, CharFilter, DateTimeFilter, ChoiceFilter, OrderingFilter, ModelChoiceFilter
from django.db.models import Q
from .models import Book, Language, BookSeries
from django.forms.widgets import TextInput, DateTimeInput, Select

class BookFilter(FilterSet):
    def __init__(self, data=None, queryset=None, *, request=None, prefix=None, **kwargs):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix, **kwargs)

        order_by_filter = self.form.fields["order"]
        order_by_filter.widget.attrs = {
            'class': 'form-select'
        }

    search = CharFilter(
        method='search_filter',
        label='Search',
        widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Search books or series...'})
    )
    series = ModelChoiceFilter(
        queryset=BookSeries.objects.all(),
        label='Series',
        widget=Select(attrs={'class': 'form-select'})
    )
    date_from = DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Date From',
        widget=DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    date_to = DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Date To',
        widget=DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )
    language = ChoiceFilter(
        choices=Language.choices,
        label='Language',
        widget=Select(attrs={'class': 'form-select'})

    )
    
    order = OrderingFilter(
        label='Sort By',
        fields=(
            ('created_at', 'created_at'),
            ('name', 'name'),
            ('series__title', 'series'),
            ('rating', 'rating'),
            ('reviews_count', 'reviews_count'),
            ('popular_reviews', 'popular_reviews'),
        ),
        field_labels={
            'created_at': 'Created Date',
            '-created_at': 'Created Date (Newest First)',
            'name': 'Name (A-Z)',
            '-name': 'Name (Z-A)',
            'series__title': 'Series (A-Z)',
            '-series__title': 'Series (Z-A)',
            'rating': 'Rating (Low to High)',
            '-rating': 'Rating (High to Low)',
            'reviews_count': 'Reviews (Least to Most)',
            '-reviews_count': 'Reviews (Most to Least)',
            'popular_reviews': 'Popular Reviews (Least to Most)',
            '-popular_reviews': 'Popular Reviews (Most to Least)',
        },
        widget=Select
    )

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(series__title__icontains=value)
        )

    class Meta:
        model = Book
        fields = ['search', 'series', 'language', 'date_from', 'date_to', 'order'] 