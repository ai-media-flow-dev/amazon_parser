from django import forms
from .models import Book, BookSeries

class BookForm(forms.ModelForm):

    series_title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    url = forms.URLField(
        max_length=1000,
        widget=forms.URLInput(attrs={'class': 'form-control'}),
    )

    def clean_url(self) -> str:
        url = self.cleaned_data.get('url')
        if url and not url.endswith('?language=en_GB'):
            raise forms.ValidationError('URL must end with ?language=en_GB')
        return url

    class Meta:
        model = Book
        fields = ['name', 'url', 'series_title', 'language']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True) -> Book:
        instance = super().save(commit=False)
        if series_title := self.cleaned_data.get('series_title'):
            series, _ = BookSeries.objects.get_or_create(title=series_title)
            instance.series = series

        if commit:
            instance.save()
        return instance
