from .models import Transaction

class FinancialSummary:
    def __init__(self,user):
        self.user = user

    def total_income(self):
        sum = (transaction.amount for transaction in Transaction.objects.filter(user=self.user,type='income',type='Income'))

        return sum
    
    def total_expense(self):
        sum = (transaction.amount for transaction in Transaction.objects.filter(user=self.user,type='expense',type='Expense'))

        return sum
    
    def net_balance(self):
        sum = self.total_income() - self.total_expense()

        return sum
            