import re
from django import forms
from .models import Book, BookSeries

class BookForm(forms.ModelForm):

    series_title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    book_id = forms.CharField(
        label='Book ID',
        max_length=1000,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    def clean(self) -> str:
        book_id = self.cleaned_data.get('book_id')
        language = self.cleaned_data.get('language')
        if language == 'en':
            language = 'com'
        complete_url = f'https://www.amazon.{language}/dp/{book_id}?language=en_GB'
        self.cleaned_data['url'] = complete_url
        return self.cleaned_data

    class Meta:
        model = Book
        fields = ['name', 'book_id', 'series_title', 'language']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True) -> Book:
        instance = super().save(commit=False)
        instance.url = self.cleaned_data.get('url')
        if series_title := self.cleaned_data.get('series_title'):
            series, _ = BookSeries.objects.get_or_create(title=series_title)
            instance.series = series

        if commit:
            instance.save()
        return instance
