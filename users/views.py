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
    return render(request, "users/login.html", context={
        "message" : "",
    })

def user_logout(request):
    return HttpResponse("meow")
