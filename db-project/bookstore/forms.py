from django import forms
from django.contrib.auth.models import User
from .models import Profile

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
