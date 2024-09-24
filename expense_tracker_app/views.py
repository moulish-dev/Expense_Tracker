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
from .models import Transaction, User

from .forms import TransactionForm, RegistrationForm, BankStatementForm,Contact_DbForm

import pandas as pd #for excel files handling
import pdfplumber #for pdf files handling
import pathlib
from pypdf import PdfReader
import re #for regex text processing
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from .utils import FinancialSummary
from django.db.models.functions import TruncMonth
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


#HTML PAGES VIEW FUNCTIONS START
def home(request):
    
    return render(request, 'public/main.html')
#HTML PAGES VIEW FUNCTIONS END

#TRANSACTION FUNCTIONS START
@login_required
def income_list(request):
    user = request.user
    summary = FinancialSummary(user)
    #filters transactions to show only income
    incomes = Transaction.objects.filter(Q(type='income') | Q(type='Income'), user=user).order_by('date')
    for transaction in incomes: 
            if transaction.type == 'income' or transaction.type == 'Income':
                transaction.symbol = '+' 
                transaction.image = 'https://cdn.pixabay.com/photo/2013/07/12/17/15/first-aid-151873_1280.png' 
            elif transaction.type == 'expense' or transaction.type == 'Expense':
                transaction.symbol = '-'
                transaction.image = 'https://cdn.pixabay.com/photo/2016/06/01/17/04/minus-1429374_1280.png' 
            else:
                transaction.symbol = 'E'
                transaction.image = ''
    
    return render(request, 'transactions/income_list.html',{
        'transactions': incomes,
        'total_income': summary.total_income(),
        'total_expense': summary.total_expense(),
        'total_balance': summary.net_balance(),
        })
@login_required
def expense_list(request):
    user = request.user
    #filters transactions to show only expenses
    expenses = Transaction.objects.filter(Q(type='Expense') | Q(type='Expense'), user=user).order_by('date')
    for transaction in expenses: 
            if transaction.type == 'income' or transaction.type == 'Income':
                transaction.symbol = '+' 
                transaction.image = 'https://cdn.pixabay.com/photo/2013/07/12/17/15/first-aid-151873_1280.png' 
            elif transaction.type == 'expense' or transaction.type == 'Expense':
                transaction.symbol = '-'
                transaction.image = 'https://cdn.pixabay.com/photo/2016/06/01/17/04/minus-1429374_1280.png' 
            else:
                transaction.symbol = 'E'
                transaction.image = ''
    summary = FinancialSummary(user)
    return render(request, 'transactions/expense_list.html', {
        'transactions': expenses,
        'total_income': summary.total_income(),
        'total_expense': summary.total_expense(),
        'total_balance': summary.net_balance(),
        })
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
    summary = FinancialSummary(user)

    return render(request, 'transactions/transaction_list.html',{
        'transactions': transactions,
        'user_name': user.username,
        'total_income': summary.total_income(),
        'total_expense': summary.total_expense(),
        'total_balance': summary.net_balance(),
        })

@login_required
def add_statement(request):
    print('Add Transaction View Accessed')
    if request.method == 'POST':
        print('POST Recieved')
        
        BankStatementform_data = BankStatementForm(request.POST, request.FILES)

        if BankStatementform_data.is_valid():
            print('BankStatementValid Confirmed')
            BankStmt = BankStatementform_data.save(commit=False)
            BankStmt.user = request.user
            BankStmt.save()
            BankStmt_file = request.FILES["file_bankstmt"]
            BankStmt_filename = BankStmt_file.name
            file_ext = pathlib.Path(BankStmt_filename).suffix
            BankStmt_file_path = default_storage.save(BankStmt_filename, ContentFile(BankStmt_file.read()))
            #Extracting data from bank statement
            #changing according to file
            try:
                if file_ext == '.pdf':
                    print('Bank Statement pdf view accessed')
                    pdf_data_list = extract_transactions_from_pdf(request.FILES["file_bankstmt"])
                    request.session['statement_transactions'] = pdf_data_list
                    print(pdf_data_list)
                    return render(request, 'transactions/confirm_transactions.html',{'pdf_transactions': pdf_data_list})
                elif file_ext == '.xlsx':
                    extract_transactions_from_xlsx(BankStmt.file) 
                    return redirect('transaction_list')
            finally:
                #deletes the uploaded file 
                if os.path.exists(BankStmt_file_path):
                    os.remove(BankStmt_file_path)
        else:
            print(BankStatementform_data.errors)
            
    else:
        print('else tried')
        BankStatementform_data = BankStatementForm()

    return render(request, 'transactions/add_statement_transaction.html', {
        'bank_statement_form' : BankStatementform_data
        })




@login_required
def add_transaction(request):
    print('Add Transaction View Accessed')
    if request.method == 'POST':
        print('POST Recieved')
        Transactionform_data = TransactionForm(request.POST)
        print(Transactionform_data)
        if Transactionform_data.is_valid():
            print('transaction add valid tried')
            transaction = Transactionform_data.save(commit=False) #not to save to database yet
            transaction.user = request.user #set the user 
            transaction.save() #save to database
            Transactionform_data.save()
            return redirect('transaction_list')
        else:
            print('valid else tried')
            print(Transactionform_data.errors)
            print(Transactionform_data.cleaned_data)
            return redirect('add_transaction')
            
    else:
        print('else tried')
        Transactionform_data = TransactionForm()
    
    summary = FinancialSummary(request.user)
    return render(request, 'transactions/add_transaction.html', {
        'transaction_form': Transactionform_data,
        'total_income': summary.total_income(),
        'total_expense': summary.total_expense(),
        'total_balance': summary.net_balance(),
        })
#TRANSACTION FUNCTIONS END

 

#BANK STATEMENT FILE HANDLING FUNCTIONS START

def extract_transactions_from_pdf(pdf_file):
    print('pdf view function accessed')
    reader = PdfReader(pdf_file)
    transactions = [] #for storing transactions
    #printing No. Of Pages
    print(len(reader.pages))
    for page in reader.pages:
        text = page.extract_text()
        transaction_pattern = re.compile(
             r'Date\n(\d{2} \w{3} \d{2})\.Description\n(.*?)\.Type\n(.*?)\.Money In \(\£\)\n(blank|\d+\.?\d*)\.Money Out \(\£\)\n(blank|\d+\.?\d*)\.Balance \(\£\)\n(\d+\.?\d*)\.',
        re.DOTALL
        )
        matches = transaction_pattern.findall(text)
        for match in matches:
            date=match[0]
            description=match[1]
            trans_type=match[2]
            money_in=match[3] if match[3] !='blank' else '0.0'
            money_out=match[4] if match[4] !='blank' else '0.0'
            balance=match[5]
            #this checks the Money_in and Money_out value in the extracted
            #text and set the transaction type as income and set the amount which is not null
            #This is done as the form submit type is different and the user can see the format
            if money_out == '0.0':
                amount_type = 'Income'
                amount = money_in
                symbol = '+'
            elif money_in == '0.0':
                amount_type = 'Expense'
                amount = money_out
                symbol = '-'
            else:
                amount_type = 'error'
                amount = 'error'
                symbol ='e'
            transactions.append({
                'Date': date,
                'Description': description,
                'Type': amount_type,
                'Amount': amount,
                'Amount_symbol': symbol,
                
            })
            
                

    return transactions
    
def remove_transactions(request):
    if request.method == "POST":
        transaction_index = int(request.POST.get('transaction_index', -1))
        transactions = request.session.get('statement_transactions',[])
        if 0<= transaction_index < len(transactions):
            del transactions[transaction_index]
            request.session['statement_transactions'] = transactions
    return render(request, 'transactions/confirm_transactions.html',{'pdf_transactions': transactions})


def add_statement_transaction(request):
    if request.method == "POST":
        transactions_data = request.session.get('statement_transactions',[])

        for transactions in transactions_data:

            date_str = transactions['Date']
            try:
                date_obj = datetime.strptime(date_str, '%d %b %y')
                formatted_date = date_obj.strftime('%Y-%m-%d')
            except ValueError as e:
                raise ValidationError(f'Invalid date format: {date_str}. Expected format is DD MMM YY.')
            print(transactions)
            Transaction.objects.create(
                date = formatted_date,
                merchant = transactions['Description'],
                type = transactions['Type'],
                amount = transactions['Amount'],
                user = request.user,
                status = 'Completed',
                category = 'category'
            )
        request.session['statement_transactions'] = []
        return redirect('transaction_list')
    return redirect('dashboard')

def extract_transactions_from_xlsx(xlsx_file):
    df = pd.read_excel(xlsx_file, skiprows=0) #using pandas to extract data

    #filter invalid rows
    df = df[df.apply(is_valid_transaction_row, axis=1)]

    #intializing list to store transactions
    transactions = []


    for _, row in df.iterrows():
        
        date=row['Date']
        merchant=row['Description']
        money_in = row['Money In'] if not pd.isna(row['Money In']) else None
        money_out = row['Money Out'] if not pd.isna(row['Money Out']) else None

        #determine the type of transaction
        if money_in:
            transaction_type = 'Income'
        elif money_out:
            transaction_type = 'Expense'
        else:
            continue

        
        transactions.append({
            'date' : date,
            'merchant' : merchant,
            'transaction_type' : transaction_type,
            'amount' : money_in if transaction_type == 'Income' else money_out
        })

    print(transactions) #test

    return transactions
        

def is_valid_transaction_row(row):
    try:
        pd.todatetime(row['Date'],format='%d/%m/%Y',errors='raise')
        return True
    except ValueError:
        return False

#BANK STATEMENT FILE HANDLING FUNCTIONS END

#USER AUTHENTICATION FUNCTIONS START
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
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
            return redirect('dashboard')
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
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')
    total_income = 0
    total_expense = 0
    for transaction in transactions: 
            if transaction.type == 'income' or transaction.type == 'Income':
                transaction.symbol = '+' 
                transaction.image = 'https://cdn.pixabay.com/photo/2013/07/12/17/15/first-aid-151873_1280.png' 
                total_income += transaction.amount
            elif transaction.type == 'expense' or transaction.type == 'Expense':
                transaction.symbol = '-'
                transaction.image = 'https://cdn.pixabay.com/photo/2016/06/01/17/04/minus-1429374_1280.png' 
                total_expense += transaction.amount
            else:
                transaction.symbol = 'E'
                transaction.image = ''
    transactions_slice = transactions[:3]
    total_balance = total_income - total_expense
    return render(request, 'transactions/dashboard.html',{
        'transactions' : transactions_slice,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance,
    })

@login_required
def profile(request):

    user=request.user
    userEmail= user.email

    return render(request, 'registration/profile.html', {
        'user': user,
        'email': userEmail,
    })

@login_required
def contactForm(request):
    if request.method == "POST":
        print('POST recieved')
        ContactFormData = Contact_DbForm(request.POST)
        if ContactFormData.is_valid():
            print('post method tried valid')
            ContactForm = ContactFormData.save(commit=False)
            ContactForm.user = request.user
            ContactForm.save()
            print('Contact Form Submitted')
            return redirect('profile')
        else:
            print('valid else tried')
            return redirect('contact-form')
    
    return render(request, 'User/user_contactform.html')

def user_help(request):
    return render(request, 'User/user_helppage.html')

def reports(request):
    user=request.user
    summary = FinancialSummary(user)
    monthly_expenses = (Transaction.objects
                        .filter(user=user,type__iexact='expense')
                        .annotate(month=TruncMonth('date'))
                        .values('month')
                        .annotate(total=Sum('amount'))
                        .order_by('month'))
    monthly_expenses_labels = [entry['month'].strftime(' %B %Y') for entry in monthly_expenses]
    monthly_expenses_data = [float(entry['total']) for entry in monthly_expenses]
    return render(request, 'transactions/reports.html',{
        'total_income':summary.total_income(),
        'total_expense':summary.total_expense(),
        'total_balance':summary.net_balance(),
        'monthly_expenses_labels':monthly_expenses_labels,
        'monthly_expenses_data': monthly_expenses_data,
        })
#USER PROFILE PAGE FUNCTIONS END
def redirect_to_homepage(request):
    return redirect('home')

def generate_statement(request):

    return render(request, 'transactions/generate_statement.html')
