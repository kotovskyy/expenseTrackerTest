from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages

from django.contrib.auth.forms import UserCreationForm
from expensetracker.models import User

from users.forms import SignupForm

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
            return HttpResponseRedirect(reverse('expensetracker_homepage'))
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
    
def user_signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request,"You have signed up successfully!")
            login(request, user)
            return HttpResponseRedirect(reverse('expensetracker_index'))
        else:
            return render(request, "users/signup.html", {
                "form" : form,
            })
        
    form = SignupForm()
    return render(request, "users/signup.html", {
        "form" : form,
    })
