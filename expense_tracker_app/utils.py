from .models import Transaction
from django.db.models import Q

class FinancialSummary:
    def __init__(self,user):
        self.user = user

    def total_income(self):
        sum_income = sum(transaction.amount for transaction in Transaction.objects.filter(type__iexact = 'income', user=self.user ))

        return sum_income
    
    def total_expense(self):
        sum_expense = sum(transaction.amount for transaction in Transaction.objects.filter(type__iexact='expense', user=self.user))

        return sum_expense
    
    def net_balance(self):
        income = self.total_income()
        expense = self.total_expense()
        sum_balance = income - expense  
        return sum_balance
            