from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('users_user-login'))
    return render(request, 'users/user.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('expensetracker_index'))
        else:
            return render(request, "users/login.html", context={
                "message": "Invalid username or password",
            })    
    return render(request, "users/login.html")

def user_logout(request):
    logout(request)
    return render(request, "users/login.html", context={
        "message": "You have been logged out successfully",
    })
