from django.shortcuts import render

#getting the Transaction Database from models.py
from .models import Transaction

def income_list(request):
    #filters transactions to show only income
    incomes = Transaction.objects.filter(type='income')
    return render(request, 'transactions/income_list.html',{'transactions': incomes})

def expense_list(request):
    #filters transactions to show only expenses
    expenses = Transaction.objects.filter(type='expense')
    return render(request, 'transactions/expense_list.html', {'transaction': expenses})


