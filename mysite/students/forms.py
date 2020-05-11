from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        submitted_data = self.cleaned_data['email']
        if all(email_domain not in submitted_data for email_domain in ['@innopolis.university', '@innopolis.ru']):
            raise forms.ValidationError('You must register using your innopolis address')
        return submitted_data
