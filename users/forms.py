from django.contrib.auth import forms
from django.contrib.auth.forms import UserCreationForm
from expensetracker.models import User

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']
