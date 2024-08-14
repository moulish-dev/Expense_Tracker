from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, JsonResponse
#to see that certain pages are only accessed by loginned users
from django.contrib.auth.decorators import login_required
#getting the Transaction Database from models.py
from .models import Transaction

from .forms import TransactionForm

#TRANSACTION FUNCTIONS START
@login_required
def income_list(request):
    #filters transactions to show only income
    incomes = Transaction.objects.filter(type='income')
    return render(request, 'transactions/income_list.html',{'transactions': incomes})
@login_required
def expense_list(request):
    #filters transactions to show only expenses
    expenses = Transaction.objects.filter(type='expense')
    return render(request, 'transactions/expense_list.html', {'transactions': expenses})
@login_required
def transactions_list(request):
    #shows all transactions
    transactions = Transaction.objects.all().order_by('date')
    return render(request, 'transactions/transaction_list.html',{'transactions': transactions})
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})
#TRANSACTION FUNCTIONS END

#USER AUTHENTICATION FUNCTIONS START
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('transaction_list')
    else:
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

def custom_login_view(request):
    
    return render(request, 'registration/login.html')

def custom_logout_view(request):
    
    return render(request, 'registration/logout.html')

#USER AUTHENTICATION FUNCTIONS END

#USER PROFILE PAGE FUNCTIONS START
@login_required
def profile(request):
    return render(request, 'registration/profile.html')
#USER PROFILE PAGE FUNCTIONS END