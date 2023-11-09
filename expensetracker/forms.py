from django import forms

from datetime import date
from .models import Account

class AddTransactionForm(forms.Form):
        
    amount = forms.DecimalField(
        label="Transaction Amount",
        max_digits=22,
        decimal_places=2
    )
    account = forms.CharField(max_length=100)
    date = forms.DateField(
        label="Date",
    )
    description = forms.CharField(
        max_length=100
    )
    
    