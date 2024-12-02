from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm  
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required #to see that certain pages are only accessed by loginned users
from .models import Transaction, User #getting the Transaction Database from models.py
from .forms import TransactionForm, RegistrationForm, BankStatementForm,Contact_DbForm
import csv
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
from reportlab.pdfgen import canvas
from statsmodels.tsa.arima.model import ARIMA
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import io
import base64


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
    expenses = Transaction.objects.filter(Q(type='expense') | Q(type='Expense'), user=user).order_by('date')
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
                    extract_transactions_from_xlsx(request.FILES["file_bankstmt"]) 
                    return redirect('transaction_list')
                elif file_ext == '.csv':
                    csv_transaction_list = extract_transactions_from_csv(BankStmt_file)
                    request.session['statement_transactions'] = csv_transaction_list
                    return render(request, 'transactions/confirm_transactions.html',{'pdf_transactions': csv_transaction_list})
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
def extract_transactions_from_csv(csv_file):
    print('CSV file statement accessed')
    transactions_csv = []
    # starting to see the data in csv file from start
    csv_file.seek(0)
    csv_file_reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
    for row in csv_file_reader:
        # mapping all the fields according to the fields name
        date = row.get('Transaction Date')
        description = row.get("Transaction Description", "")
        debit_amount = row.get("Debit Amount", "").strip()
        credit_amount = row.get("Credit Amount", "").strip()
        
        # Determine transaction type and amount to seperate all the debit and credit
        # changing this to change 
        if debit_amount:
            amount = float(debit_amount)
            type = "expense"
        elif credit_amount:
            amount = float(credit_amount)
            type = "income"
        else:
            continue  # Skipping the rows with no valid amount
        
        transactions_csv.append({
                'Date': date,
                'Description': description,
                'Type': type,
                'Amount': amount,
            })
    return transactions_csv
    
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
                date_obj = parse_date(date_str) #will access the date format
                # using because many date formats arise
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
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        file_type = request.POST.get('file_type')
        
        # parsing all dates into one using parse_date() function
        try:
            from_date = parse_date(from_date)
            to_date = parse_date(to_date)
        except ValueError:
            return HttpResponse("Invalid date format", status=400)
        
        user = request.user
        requested_transactions = Transaction.objects.filter(
            user=user,
            date__range=(from_date, to_date)
        ).values('date', 'merchant', 'type', 'amount', 'category', 'status')
        
        if file_type == 'excel':
            # Generate Excel file
            df = pd.DataFrame(list(requested_transactions))

            # Create an in-memory buffer
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Financial Statement', index=False)

            # Get the base64-encoded file content
            buffer.seek(0)
            file_content = base64.b64encode(buffer.read()).decode()

            # Prepare the context for HTML rendering
            context = {
                'file_type': 'excel',
                'file_content': file_content,
                'file_name': 'financial_statement.xlsx'
            }

            return render(request, 'transactions/generate_statement.html', context)

        elif file_type == 'pdf':
            # Generate PDF file
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)

            # Title
            p.setFont("Helvetica-Bold", 16)
            p.drawString(100, 800, f"Financial Statement: {from_date} to {to_date}")

            # Create table-like headers
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, 770, "Date")
            p.drawString(150, 770, "Merchant")
            p.drawString(300, 770, "Type")
            p.drawString(400, 770, "Amount")

            # Loop through transactions
            y = 750
            p.setFont("Helvetica", 10)
            for transaction in requested_transactions:
                p.drawString(50, y, str(transaction['date']))
                p.drawString(150, y, transaction['merchant'])
                p.drawString(300, y, transaction['type'])
                p.drawString(400, y, f"{transaction['amount']:.2f}")
                y -= 20

                # Page breaking mechanism
                if y < 50:
                    p.showPage()
                    p.setFont("Helvetica", 10)
                    y = 800

            p.showPage()
            p.save()
            buffer.seek(0)

            # Get the base64-encoded file content
            file_content = base64.b64encode(buffer.read()).decode()

            # Prepare the context for HTML rendering
            context = {
                'file_type': 'pdf',
                'file_content': file_content,
                'file_name': 'financial_statement.pdf'
            }

            return render(request, 'transactions/generate_statement.html', context)
        
    return render(request, 'transactions/generate_statement.html')


def parse_date(date_str):
    # these are the list of date formats which will be supported
    # used in function add_statement transaction
    date_formats = [
        '%d/%m/%Y',  # 29/11/2024
        '%d-%m-%Y',  # 29-11-2024
        '%Y-%m-%d',  # 2024-11-29
        '%d %b %Y',  # 29 Nov 2024
        '%d %B %Y',  # 29 November 2024
        '%d-%b-%y',  # 29-Nov-24
        '%d/%b/%Y',  # 29/Nov/2024
    ]

    # trying to parse all date formats will return the one needed
    for date_format in date_formats:
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError:
            continue

    # If no format works here a validation error is raised
    raise ValidationError(f"Invalid date format: {date_str}. Supported formats are: {', '.join(date_formats)}")

# Forecasting Future Transactions
# All the transactions of the user is bundled into one
def bundle_transaction_data(user):
    #the user is taken as parameter and used as index to pull user's transactions
    bundle_transactions = Transaction.objects.filter(user=user).order_by('date')
    data = []
    # changing all the amount number into negative for expenses 
    # all the transactions are added into data[] list
    for transaction in bundle_transactions:
        if transaction.type.lower() == 'expense':
            data.append({'date': transaction.date, 'amount': -transaction.amount})
        else:
            data.append({'date': transaction.date, 'amount': transaction.amount})
            
    data_df = pd.DataFrame(data)
    # converting all date into datetime format if error arises even though already converted
    data_df['date'] = pd.to_datetime(data_df['date']) 
    data_df.set_index('date',inplace=True) #setting index while in use
    
    return data_df

@login_required
def forecast_transactions(request):
    user = request.user
    data_df = bundle_transaction_data(user)
    #data preprocessing
    data_df['amount'] = pd.to_numeric(data_df['amount'], errors='coerce')
    data_df = data_df.dropna(subset=['amount'])
    # resampling all the data for daily, weekly, monthly data
    daily_df = data_df.resample('D').sum()
    weekly_df = data_df.resample('W').sum()
    monthly_df = data_df.resample('M').sum()
    
    try:
        model = ARIMA(daily_df['amount'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=10)
        daily_forecast = {
            'labels': forecast.index.strftime('%Y-%m-%d').tolist(),
            'data': forecast.values.tolist()
        }
    except Exception as e:
        daily_forecast = {'error': str(e)}

    try:
        model = ARIMA(weekly_df['amount'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=10)
        weekly_forecast = {
            'labels': forecast.index.strftime('%Y-%m-%d').tolist(),
            'data': forecast.values.tolist()
        }
    except Exception as e:
        weekly_forecast = {'error': str(e)}

    try:
        model = ARIMA(monthly_df['amount'], order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=10)
        monthly_forecast = {
            'labels': forecast.index.strftime('%Y-%m-%d').tolist(),
            'data': forecast.values.tolist()
        }
    except Exception as e:
        monthly_forecast = {'error': str(e)}

    forecasts = {
        'daily': daily_forecast,
        'weekly': weekly_forecast,
        'monthly': monthly_forecast
    }

    return render(request, 'transactions/forecast_transactions.html', {'forecasts': forecasts })
    
