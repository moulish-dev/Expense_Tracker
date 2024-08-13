
from django.urls import path
from . import views

urlpatterns = [
    path('income/', views.income_list, name='income_list'),
    path('expense/',views.expense_list, name='expense_list'),
    path('transactions/',views.transactions_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
]