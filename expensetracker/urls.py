from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='expensetracker_index'),
    path('homepage/', views.homepage, name='expensetracker_homepage'),
    path('homepage/<int:category_id>/', views.category_page, 
         name='expensetracker_category-page'),
    path('accounts/', views.accounts_page, 
         name='expensetracker_accounts-page'),
    path('transactions/', views.transactions_page, 
         name='expensetracker_transactions-page'),
    path('transactions/<int:transaction_id>/', views.transaction_edit_page,
         name='expensetracker_transaction-edit-page'),
    path('transactions/<int:transaction_id>/delete/', views.transaction_delete,
         name='expensetracker_transaction-delete')
]
