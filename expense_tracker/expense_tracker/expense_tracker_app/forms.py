from django import forms
from .models import Transaction, BankStatement
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        fields = ['type','category','amount','date', 'time', 'merchant', 'status',
                  'description']
    def save(self, commit=True, user=None):
        transaction = super().save(commit=False)
        if user:
            transaction.user = user
        if commit:
            transaction.save()
        return transaction

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','email','password1','password2']


class BankStatementForm(forms.ModelForm):
    class Meta:
        model=BankStatement
        fields=['file_bankstmt']
    