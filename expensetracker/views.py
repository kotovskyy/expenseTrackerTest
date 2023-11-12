from django.shortcuts import render, redirect

from .models import Account, Category, Settings, Transaction, Currency

from .forms import AddTransactionForm

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
    
    categories = Category.objects.filter(user=user)
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
    transactions = Transaction.objects.filter(user=user, category=category)
    if request.method == "POST":
        form = AddTransactionForm(user, request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            date = form.cleaned_data["date"]
            description = form.cleaned_data["description"]
            account_id = form.cleaned_data["account"]
            account = user.accounts.filter(id=account_id).first()
            
            transaction = Transaction.objects.create(
                user=user,
                account=account,
                category=category,
                transaction_type=category.category_type,
                amount=amount,
                currency=user.settings.first().main_currency,
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
