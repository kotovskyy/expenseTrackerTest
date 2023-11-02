from django.shortcuts import render

from .models import Account

# Create your views here.
def index(request):
    return render(request, 'expensetracker/index.html', context={
        "accounts":Account.objects.all()
    })
