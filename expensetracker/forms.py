from django import forms

from datetime import date
from .models import Account, Currency

class AddTransactionForm(forms.Form):
        
    amount = forms.DecimalField(
        label="Transaction Amount",
        max_digits=22,
        decimal_places=2
    )
    currency = forms.ChoiceField(
        choices=[(c.id, c.code) for c in Currency.objects.all()],
        initial=None
    )
    account = forms.ChoiceField(choices=[])
    date = forms.DateField(
        label="Date",
        initial=date.today(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    description = forms.CharField(
        max_length=100
    )
    
    def __init__(self, user, *args, **kwargs):
        super(AddTransactionForm, self).__init__(*args, **kwargs)
        self.fields['account'].choices = \
            [(acc.id, acc.name) for acc in user.accounts.filter(user=user)]
        self.fields['currency'].initial = user.settings.first().main_currency
        
        
class EditTransactionForm(forms.Form):
        
    amount = forms.DecimalField(
        label="Amount",
        max_digits=22,
        decimal_places=2
    )
    currency = forms.ChoiceField(
        choices=[(c.id, c.code) for c in Currency.objects.all()],
    )
    account = forms.ChoiceField(choices=[])
    category = forms.ChoiceField(choices=[])
    date = forms.DateField(
        label="Date",
        initial=date.today(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    description = forms.CharField(
        max_length=100
    )
    
    def __init__(self, user, *args, **kwargs):
        super(EditTransactionForm, self).__init__(*args, **kwargs)
        self.fields['account'].choices = \
            [(acc.id, acc.name) for acc in user.accounts.filter(user=user)]
        self.fields['category'].choices = \
            [(c.id, c.name) for c in user.categories.filter(user=user)]
        self.fields['currency'].initial = user.settings.first().main_currency
        

class EditAccountForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        initial=None
    )
    balance = forms.DecimalField(
        max_digits=22,
        decimal_places=2
    )
    currency = forms.ChoiceField(
        choices=[(c.id, c.code) for c in Currency.objects.all()]
    )
    description = forms.CharField(
        max_length=100
    )


class AddCategoryForm(forms.Form):
    INCOME = "I"
    EXPENSE = "E"
    name = forms.CharField(
        max_length=50
    )
    category_type = forms.ChoiceField(
        choices=[(EXPENSE, "Expense"), (INCOME, "Income")],
        initial=EXPENSE
    )
    
class AddIncomeToAccountForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=22,
        decimal_places=2
    )
    currency = forms.ChoiceField(
        choices=[(c.id, c.code) for c in Currency.objects.all()],
    )
    category = forms.ChoiceField(
        label="Income category",
        choices=[]
    )
    date = forms.DateField(
        label="Date",
        initial=date.today(),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    description = forms.CharField(
        max_length=100
    )
    
    def __init__(self, user, *args, **kwargs):
        super(AddIncomeToAccountForm, self).__init__(*args, **kwargs)
        self.fields['category'].choices = \
            [(c.id, c.name) for c in user.categories.filter(category_type="I")]
        self.fields['currency'].initial = user.settings.first().main_currency
    
    