from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    #transaction type tuple to diffrentiate income and expense
    TRANSACTION_TYPES = (
        ('income','Income'),
        ('expense','Expense'),
    )
    STATUS = (
        ('completed','Completed'),
        ('scheduled', 'Scheduled'),
    )
    #to manage the users for each
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #amount variable to store the expense and income
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #type of the transaction determined from TRANSACTION_TYPES
    type = models.CharField(max_length=7,choices=TRANSACTION_TYPES)
    #category of the transaction like Food,Transport
    category = models.CharField(max_length=50,null=True)
    #description of the transaction
    description = models.TextField(blank=True,null=True)
    date = models.DateField(blank=True,null=True)
    time = models.TimeField(blank=True,null=True)
    merchant = models.CharField(max_length=20,default='merchant')
    status = models.CharField(max_length=9,choices=STATUS,default='completed')
    

    def __str__(self):
        return f"{self.get_type_display()} - {self.category}: ${self.amount}"

class BankStatement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file_bankstmt = models.FileField()
    uploaded_at = models.DateTimeField(auto_now_add=True)


