from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='users_index'),
    path('login/', views.user_login, name='users_user-login'),
    path('logout/', views.user_logout, name='users_user-logout')
]
