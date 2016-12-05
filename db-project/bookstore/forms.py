from django import forms
from django.contrib.auth.models import User
from .models import Profile, Book
from django.forms.extras import SelectDateWidget

class SearchForm(forms.Form):
    search_value = forms.CharField(label='Search', max_length=100)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']


class ProfileForm(forms.ModelForm):
    credit_card_number = forms.CharField(min_length=16, max_length=16, required=True)

    class Meta:
        model = Profile
        fields = ['credit_card_number', 'mailing_address', 'phone_number']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class NewBookForm(forms.ModelForm):
    isbn13 = forms.CharField(label='ISBN13', min_length=13, max_length=13)
    isbn10 = forms.CharField(label='ISBN10', min_length=10, max_length=10)
    class Meta:
        model = Book
        fields = '__all__'

class AddCopiesForm(forms.Form):
    isbn13 = forms.CharField(label='ISBN13', min_length=13, max_length=13)
    num_copies = forms.IntegerField(label='Copies to add')

class StatisticsForm(forms.Form):
    month_choices = (
        ('1', 'Jan'),
        ('2', 'Feb'),
        ('3', 'Mar'),
        ('4', 'Apr'),
        ('5', 'May'),
        ('6', 'Jun'),
        ('7', 'Jul'),
        ('8', 'Aug'),
        ('9', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec')
    )

    month = forms.ChoiceField(choices=month_choices)
    view_top = forms.IntegerField(min_value=1)
