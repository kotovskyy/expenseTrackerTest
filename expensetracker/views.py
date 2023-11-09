from django.shortcuts import render, redirect

from .models import Account, Category, Settings, Transaction

from .forms import AddTransactionForm

# Create your views here.
def index(request):
    return render(request, 'expensetracker/index.html', context={
        "accounts":Account.objects.all(),
        "categories":Category.objects.all(),
    })
    
def homepage(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    total_expenses = transactions.filter(transaction_type="E")
    total_expenses = sum([t.amount for t in total_expenses])
    total_income = transactions.filter(transaction_type="I")
    total_income = sum([t.amount for t in total_income])
    
    return render(request, 'expensetracker/homepage.html', context={
        "categories":Category.objects.filter(user=user),
        "settings": Settings.objects.get(user=user),
        "total_expenses": total_expenses,
        "total_income": total_income,
    })
    
def category_page(request, category_id):
    user = request.user
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