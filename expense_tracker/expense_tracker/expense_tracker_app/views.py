from django.shortcuts import render, redirect

#getting the Transaction Database from models.py
from .models import Transaction

from .forms import TransactionForm

def income_list(request):
    #filters transactions to show only income
    incomes = Transaction.objects.filter(type='income')
    return render(request, 'transactions/income_list.html',{'transactions': incomes})

def expense_list(request):
    #filters transactions to show only expenses
    expenses = Transaction.objects.filter(type='expense')
    return render(request, 'transactions/expense_list.html', {'transactions': expenses})

def transactions_list(request):
    #shows all transactions
    transactions = Transaction.objects.all().order_by('date')
    return render(request, 'transactions/transaction_list.html',{'transactions': transactions})

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})