from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='expensetracker_index'),
    path('homepage/', views.homepage, name='expensetracker_homepage'),
    path('homepage/<int:category_id>/', views.category_page, name='expensetracker_category-page'),
]
