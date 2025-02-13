
from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='blank'),
    path('home/', views.home, name='home'),
    path('income/', views.income_list, name='income_list'),
    path('expense/',views.expense_list, name='expense_list'),
    path('transactions/',views.transactions_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard' ),
    path('profile/', views.profile, name='profile'),
    path('remove_transaction/', views.remove_transactions , name='remove_transaction'),
    path('add_statement_transaction/', views.add_statement_transaction, name='add_statement_transaction'),
    path('contact-form/', views.contactForm, name='contact-form'),
    path('add_statement/',views.add_statement, name='add_statement_form'),
    path('help/',views.user_help,name='help'),
    path('reports/',views.reports,name='reports'),
    path('forecast_transactions/', views.forecast_transactions, name='forecast_transactions'),
    path('generate_statement',views.generate_statement,name='generate_statement')
    ]