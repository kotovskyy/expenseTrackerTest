from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

from .models import Account, Category, Settings, Transaction, Currency

from .forms import (AddTransactionForm,
                    EditTransactionForm,
                    EditAccountForm,
                    AddCategoryForm,
                    AddIncomeToAccountForm)

from decimal import Decimal
import datetime
import calendar

def convert_amount(amount, currency, main_currency):
    rate = currency.exchange_rates[main_currency.code]
    rate = Decimal(str(rate))
    return round(amount * rate, 2)

def transaction_dates(transactions):
    dates = [
        (d[0].strftime("%A"),
        d[0].day,
        d[0].strftime("%B"),
        d[0].year,
        d[0]) for d in transactions.distinct().values_list("date")]
    date_transactions = {date:[] for date in dates}
    for date in dates:
        for t in transactions:
            if t.date == date[4]:
                date_transactions[date].append(t)
    return date_transactions
    
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

    # get period of time (month) to filter data
    month_number = int(request.GET.get('month', datetime.date.today().month))
    year = int(request.GET.get('year', datetime.date.today().year))
    month_name = calendar.month_name[month_number]
    
    
    income_transactions = Transaction.objects.filter(
        user=user,
        date__month=month_number,
        date__year=year,
        transaction_type="I"
    )

    total_income = sum([t.amount for t in income_transactions])
    
    categories = Category.objects.filter(user=user, category_type="E").order_by('id')
    settings = Settings.objects.get(user=user)
    
    categories_total = []
    main_currency = user.settings.get(user=user).main_currency
    
    for c in categories:
        transactions = c.transactions.filter(
            date__month=month_number,
            date__year=year
        )
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
        "month_name": month_name,
        "year":year,
    })

def add_new_category(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    if request.method == "POST":
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            cat_type = form.cleaned_data["category_type"]
            total = Decimal("0")
            
            category = Category.objects.create(
                user=user,
                name=name,
                category_type=cat_type,
                total=total
            )
            
        else:
            return render(request, 'expensetracker/add_category_page.html', context={
                "form": form,
            })
            
    form = AddCategoryForm()
    return render(request, 'expensetracker/add_category_page.html', context={
        "form": form,
    })
    
def remove_category(request, category_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    main_currency = user.settings.get(user=user).main_currency
    category = user.categories.get(id=category_id)
    transactions = category.transactions.all()
    if request.method == 'POST':
        for t in transactions:
            account = t.account
            amount = t.amount
            currency = t.currency
            amount_converted = convert_amount(amount, currency, main_currency)
            
            sign = -1 if t.transaction_type == "I" else 1
            
            account.balance += sign * amount_converted

            account.save()
            
            t.delete()
        
        category.delete()
        return redirect(homepage)
    
    return HttpResponseBadRequest("Invalid request")
    
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
    date_transactions = transaction_dates(transactions)
    
    return render(request, 'expensetracker/category.html', context={
        "category": category,
        "form": form,
        "date_transactions": date_transactions,
        "ntransactions": transactions.count(),
    })
    
def accounts_page(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    accounts = user.accounts.all().order_by('id')
    return render(request, 'expensetracker/accounts.html', context={
        "accounts": accounts,
    })


def transactions_page(request):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    transactions = user.transactions.all().order_by('date').reverse()    
    date_transactions = transaction_dates(transactions)
                
    return render(request, 'expensetracker/transactions.html', context={
        "transactions": transactions,
        "date_transactions": date_transactions,
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
        else:
            return render(request, 'expensetracker/transaction.html', context={
                'transaction': transaction,
                'form': form,
            })
            
    
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

def account_page(request, account_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    
    account = user.accounts.get(id=account_id)
    transactions= account.transactions.all().order_by('date').reverse()
    date_transactions = transaction_dates(transactions)
    incomeform = AddIncomeToAccountForm(user)
     
    if request.method == 'POST':
        editform = EditAccountForm(request.POST)
        if editform.is_valid():
            new_name = editform.cleaned_data['name']
            new_balance = editform.cleaned_data['balance']
            new_currency_id = editform.cleaned_data['currency']
            new_description = editform.cleaned_data['description']
            new_currency = Currency.objects.get(id=new_currency_id)
            
            account.name = new_name
            account.balance = new_balance
            account.currency = new_currency
            account.description = new_description
            
            account.save()
            
            return redirect(accounts_page)
            
        else:
            return render(request, 'expensetracker/account.html', context={
                "account":account,
                "editform": editform,
                "incomeform": incomeform,
                "date_transactions": date_transactions,
            })
        
    
    
    editform = EditAccountForm()
    
    editform.fields['balance'].initial = account.balance
    editform.fields['currency'].initial = account.currency.id
    editform.fields['description'].initial = account.description
    editform.fields['name'].initial = account.name
    
    
    return render(request, 'expensetracker/account.html', context={
        "account":account,
        "editform": editform,
        "incomeform": incomeform,
        "date_transactions": date_transactions,
    })

def add_account_income(request, account_id):
    user = request.user
    if not user.is_authenticated:
        return redirect(index)
    
    account = user.accounts.get(id=account_id)
    
    transactions= account.transactions.all().order_by('date').reverse()
    date_transactions = transaction_dates(transactions)
    
    editform = EditAccountForm()
    
    editform.fields['balance'].initial = account.balance
    editform.fields['currency'].initial = account.currency.id
    editform.fields['description'].initial = account.description
    editform.fields['name'].initial = account.name
    
    if request.method == 'POST':
        form = AddIncomeToAccountForm(user, request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            currency_id = form.cleaned_data["currency"]
            category_id = form.cleaned_data["category"]
            date = form.cleaned_data["date"]
            description = form.cleaned_data["description"]
            category = user.categories.get(id=category_id)
            currency = Currency.objects.get(id=currency_id)
            
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
            
            if account.currency == currency:
                account.balance += amount
            else:
                converted_amount = convert_amount(amount, currency, account.currency)
                account.balance += converted_amount
            
            main_currency = user.settings.get(user=user).main_currency
            converted_amount = convert_amount(amount, currency, main_currency)
            category.total += converted_amount
            
            account.save()
            category.save()
            
            return render(request, 'expensetracker/account.html', context={
                "account":account,
                "editform": editform,
                "incomeform": AddIncomeToAccountForm(user),
                "date_transactions": date_transactions,
            })
            
            
        else:
            return render(request, 'expensetracker/account.html', context={
                "account":account,
                "editform": editform,
                "incomeform": form,
                "date_transactions": date_transactions,
            })
    
        
    return HttpResponseBadRequest("Invalid request")
