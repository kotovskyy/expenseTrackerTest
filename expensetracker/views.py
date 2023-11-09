from django.shortcuts import render

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
    category = Category.objects.get(id=category_id)
    if request.method == "POST":
        form = AddTransactionForm(request.POST)
        amount = form["amount"]
        date = form.date
        description = form.description
        user = request.user
        account_name = form.account
        account = user.accounts.objects.filter(name=account_name)
        
        # transaction = Transaction()
        
        account.balance = account.balance - amount
        account.save()
        category.total += amount
        category.save()
        
    
    form = AddTransactionForm()
    return render(request, 'expensetracker/category.html', context={
        "category": category,
        "form": form
    })