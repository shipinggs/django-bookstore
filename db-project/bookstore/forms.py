from django import forms

class SearchForm(forms.Form):
    search_value = forms.CharField(label='Search', max_length=100)
