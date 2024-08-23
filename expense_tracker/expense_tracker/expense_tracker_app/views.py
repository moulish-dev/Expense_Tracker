from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
#to see that certain pages are only accessed by loginned users
from django.contrib.auth.decorators import login_required
#getting the Transaction Database from models.py
from .models import Transaction

from .forms import TransactionForm, RegistrationForm

#HTML PAGES VIEW FUNCTIONS START
def home(request):
    
    return render(request, './home.html')
#HTML PAGES VIEW FUNCTIONS END
#TRANSACTION FUNCTIONS START
@login_required
def income_list(request):
    user = request.user
    #filters transactions to show only income
    incomes = Transaction.objects.filter(type='income', user=user).order_by('date')
    return render(request, 'transactions/income_list.html',{'transactions': incomes})
@login_required
def expense_list(request):
    user = request.user
    #filters transactions to show only expenses
    expenses = Transaction.objects.filter(type='expense', user=user).order_by('date')
    return render(request, 'transactions/expense_list.html', {'transactions': expenses})
@login_required
def transactions_list(request):
    #shows all transactions
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('date')
    for transaction in transactions: 
            if transaction.type == 'income' or transaction.type == 'Income':
                transaction.symbol = '+' 
                transaction.image = 'https://cdn.pixabay.com/photo/2013/07/12/17/15/first-aid-151873_1280.png' 
            elif transaction.type == 'expense' or transaction.type == 'Expense':
                transaction.symbol = '-'
                transaction.image = 'https://cdn.pixabay.com/photo/2016/06/01/17/04/minus-1429374_1280.png' 
            else:
                transaction.symbol = 'E'
                transaction.image = ''
    context = {'transactions': transactions}        

    
    return render(request, 'transactions/transaction_list.html',{
        'transactions': transactions,
        'user_name': user.username})
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False) #not to save to database yet
            transaction.user = request.user #set the user 
            transaction.save() #save to database
            form.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})
#TRANSACTION FUNCTIONS END

#USER AUTHENTICATION FUNCTIONS START
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('transaction_list')
        else:
            return render(request, 'registration/register.html', {'form': form})  # Re-render the form with errors
    else:
        form = RegistrationForm()
        return render(request, 'registration/register.html', {'form': form})

def custom_login_view(request):
    if request.method == 'POST':
        #extract username or email and password
        username_or_email = request.POST.get('username', '')
        password = request.POST.get('password','')
        #get user model
        User = get_user_model()
        #check if input is email address
        if '@' in username_or_email:
            try:
                #try to find user by email
                user = User.objects.get(email=username_or_email)
                #authenticate using username with the email
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                user=None
        else:
            #Authenticate using username
            user = authenticate(username=username_or_email,password=password) 

        
        if user is not None:
            auth_login(request, user)
            return redirect('transaction_list')
        else:
            print("Login failed. Re-rendering login form.")
            form = AuthenticationForm()
            return render(request, 'registration/login.html', {'form': form})
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def custom_logout_view(request):
    
    return render(request, 'registration/logout.html')

#USER AUTHENTICATION FUNCTIONS END

#USER PROFILE PAGE FUNCTIONS START
@login_required
def dashboard(request):
    return render(request, 'transactions/dashboard.html')
#USER PROFILE PAGE FUNCTIONS END