from django.db import models

class Transaction(models.Model):
    #transaction type tuple to diffrentiate income and expense
    TRANSACTION_TYPES = (
        ('income','Income'),
        ('expense','Expense'),
    )

    #amount variable to store the expense and income
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    #type of the transaction determined from TRANSACTION_TYPES
    type = models.CharField(max_length=7,choices=TRANSACTION_TYPES)
    #category of the transaction like Food,Transport
    category = models.CharField(max_length=50)
    #description of the transaction
    description = models.TextField(blank=True,null=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.get_type_display()} - {self.category}: ${self.amount}"


