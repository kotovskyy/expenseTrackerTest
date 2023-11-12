from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

from .models import Account, Category, Settings, Transaction, Currency

from .forms import AddTransactionForm, EditTransactionForm

from decimal import Decimal

def convert_amount(amount, currency, main_currency):
    rate = currency.exchange_rates[main_currency.code]
    rate = Decimal(str(rate))
    return round(amount * rate, 2)
    
# Create your views here.
def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect(homepage)
    return render(request, 'expensetracker/index.html', context={
        "accounts":Account.objects.all(),
        "categories":Category.objects.all(),
    })
    
def homepage(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    transactions = Transaction.objects.filter(user=user)
    total_expenses = transactions.filter(transaction_type="E")
    total_expenses = sum([t.amount for t in total_expenses])
    total_income = transactions.filter(transaction_type="I")
    total_income = sum([t.amount for t in total_income])
    
    categories = Category.objects.filter(user=user).order_by('id')
    settings = Settings.objects.get(user=user)
    
    categories_total = []
    main_currency = user.settings.get(user=user).main_currency
    
    for c in categories:
        transactions = c.transactions.all()
        total = 0
        for t in transactions:
            total += convert_amount(t.amount, t.currency, main_currency)
        categories_total.append(total)

    total_expenses = sum(categories_total)
    categories_expenses = list(zip(categories, categories_total))            
    
    return render(request, 'expensetracker/homepage.html', context={
        "categories":categories,
        "cat_expenses":categories_expenses,
        "settings": settings,
        "total_expenses": total_expenses,
        "total_income": total_income,
    })
    
def category_page(request, category_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    category = Category.objects.get(id=category_id)
    transactions = category.transactions.all().order_by('date').reverse()
    if request.method == "POST":
        form = AddTransactionForm(user, request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            date = form.cleaned_data["date"]
            description = form.cleaned_data["description"]
            account_id = form.cleaned_data["account"]
            currency_id = form.cleaned_data["currency"]
            account = user.accounts.filter(id=account_id).first()
            currency = Currency.objects.filter(id=currency_id).first()
            
            transaction = Transaction.objects.create(
                user=user,
                account=account,
                category=category,
                transaction_type=category.category_type,
                amount=amount,
                currency=currency,
                date=date,
                description=description
            )
            
            if category.category_type == 'E':
                account.balance -= amount
            else:
                account.balance += amount
            
            category.total += amount
            
            account.save()
            category.save()
            
        else:
            return render(request, 'expensetracker/category.html', context={
                "category": category,
                "form": form,
                "transactions": transactions,
            })
                   
    form = AddTransactionForm(user=user)
    return render(request, 'expensetracker/category.html', context={
        "category": category,
        "form": form,
        "transactions": transactions, 
    })
    
def accounts_page(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    accounts = user.accounts.all()
    return render(request, 'expensetracker/accounts.html', context={
        "accounts": accounts,
    })


def transactions_page(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    transactions = user.transactions.all()
    return render(request, 'expensetracker/transactions.html', context={
      "transactions": transactions,  
    })
    
def transaction_edit_page(request, transaction_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    transaction = user.transactions.filter(id=transaction_id).first()
    if request.method == 'POST':
        form = EditTransactionForm(user, request.POST)
        if form.is_valid():
            new_amount = form.cleaned_data['amount']
            new_date = form.cleaned_data['date']
            new_description = form.cleaned_data['description']
            new_account_id = form.cleaned_data['account']
            new_currency_id = form.cleaned_data['currency']
            new_category_id = form.cleaned_data['category']
            new_account = user.accounts.filter(id=new_account_id).first()
            new_currency = Currency.objects.get(id=new_currency_id)
            new_category = user.categories.filter(id=new_category_id).first()
            
            sign = -1 if transaction.transaction_type == "I" else 1
            
            orig_account = transaction.account
            orig_category = transaction.category
            
            # save changes to the database
            if orig_account != new_account:
                # update original account's balance dep. on transaction type
                # if t.type was expense/transfer -> increase orig_account balance
                # if t.type was income -> decrease orig_account balance
                orig_account.balance += sign * transaction.amount
                # update new account's balance
                new_account.balance -= sign * new_amount
                orig_account.save()
                new_account.save()
            else:
                orig_account.balance += sign * transaction.amount
                # update new account's balance
                orig_account.balance -= sign * new_amount
                orig_account.save()
                
                
            if orig_category != new_category:
                # update categories total value
                orig_category.total += sign * transaction.amount
                new_category.total -= sign * new_amount
                orig_category.save()
                new_category.save()
            else:
                orig_category.total += sign * transaction.amount
                orig_category.total -= sign * new_amount
                orig_category.save()
                
        
            # update transaction's data
            transaction.amount = new_amount
            transaction.date = new_date
            transaction.currency = new_currency
            transaction.description = new_description
            transaction.account = new_account
            transaction.category = new_category

            transaction.save()
            
    
    form = EditTransactionForm(user=user)
    form.fields['amount'].initial = transaction.amount
    form.fields['currency'].initial = transaction.currency.id
    form.fields['date'].initial = transaction.date
    form.fields['category'].initial = transaction.category.id
    form.fields['description'].initial = transaction.description
    form.fields['account'].initial = transaction.account.id
    
    return render(request, 'expensetracker/transaction.html', context={
        'transaction': transaction,
        'form': form,
    })
    

def transaction_delete(request, transaction_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    main_currency = user.settings.get(user=user).main_currency
    transaction = user.transactions.get(id=transaction_id)
    if request.method == 'POST':
        category = transaction.category
        account = transaction.account
        amount = transaction.amount
        currency = transaction.currency
        amount_converted = convert_amount(amount, currency, main_currency)
        
        sign = -1 if transaction.transaction_type == "I" else 1
        
        account.balance += sign * amount_converted
        category.total -= amount_converted
        
        account.save()
        category.save()
        transaction.delete()
        return redirect(transactions_page)
    return HttpResponseBadRequest("Invalid request")
