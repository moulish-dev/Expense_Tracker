from django.test import TestCase

# Create your tests here.

import pytest
from datetime import datetime
from django.core.exceptions import ValidationError
from expense_tracker_app.views import parse_date, extract_transactions_from_csv, extract_transactions_from_pdf, extract_transactions_from_xlsx  # replace 'your_app' with the correct app name
from django.core.files.uploadedfile import SimpleUploadedFile
from expense_tracker_app.models import Transaction
from django.contrib.auth.models import User
from django.test import Client
import os


@pytest.mark.parametrize("date_str, expected_date", [
    ("29/11/2024", datetime(2024, 11, 29)),
    ("29-11-2024", datetime(2024, 11, 29)),
    ("2024-11-29", datetime(2024, 11, 29)),
    ("29 Nov 2024", datetime(2024, 11, 29)),
    ("29 November 2024", datetime(2024, 11, 29)),
    ("29-Nov-24", datetime(2024, 11, 29)),
    ("29/Nov/2024", datetime(2024, 11, 29)),
])
def test_parse_date_valid_formats(date_str, expected_date):
    # Test that valid date formats are parsed correctly
    parsed_date = parse_date(date_str)
    assert parsed_date == expected_date


@pytest.mark.parametrize("invalid_date_str", [
    "11/29/2024",  # Invalid format MM/DD/YYYY
    "2024/11/29",  # Invalid separator
    "29.11.2024",  # Unsupported separator
    "Nov 29 2024", # Unsupported format
    "2024-29-11",  # Incorrect order
])
def test_parse_date_invalid_formats(invalid_date_str):
    # Test that invalid date formats raise a ValidationError
    with pytest.raises(ValidationError):
        parse_date(invalid_date_str)


def test_parse_date_empty_string():
    # Test that an empty string raises a ValidationError
    with pytest.raises(ValidationError):
        parse_date("")


def test_parse_date_none():
    # Test that None raises a ValidationError
    with pytest.raises(ValidationError):
        parse_date(None)


# Bank Statement Extraction Tests
def test_extract_transactions_from_csv():
    csv_content = """Transaction Date,Transaction Description,Debit Amount,Credit Amount
    29/11/2024,Test Merchant,100.0,
    30/11/2024,Another Merchant,,50.0
    """
    csv_file = SimpleUploadedFile("test.csv", csv_content.encode('utf-8'), content_type="text/csv")
    transactions = extract_transactions_from_csv(csv_file)
    assert len(transactions) == 2
    assert transactions[0]['Type'] == "expense"
    assert transactions[1]['Type'] == "income"


def test_extract_transactions_from_pdf():
    pdf_path = "tests/test_files/sample_bank_statement.pdf"
    with open(pdf_path, "rb") as pdf_file:
        transactions = extract_transactions_from_pdf(pdf_file)
        assert isinstance(transactions, list)
        # Add assertions based on the known content of the test PDF


def test_extract_transactions_from_xlsx():
    xlsx_path = "tests/test_files/sample_bank_statement.xlsx"
    with open(xlsx_path, "rb") as xlsx_file:
        transactions = extract_transactions_from_xlsx(xlsx_file)
        assert isinstance(transactions, list)
        # Add assertions based on the known content of the test XLSX


# Transaction Handling Tests@pytest.mark.django_db
def test_add_transaction_view(client):
    user = User.objects.create_user(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")
    response = client.post("/add_transaction/", {
        "merchant": "Test Merchant",
        "category": "Test Category",
        "type": "income",
        "amount": 100.0,
        "status": "completed",
        "date": "2024-11-29",
        "time": "12:00",
    })
    assert response.status_code == 302  # Redirects after successful addition
    assert Transaction.objects.filter(user=user, merchant="Test Merchant").exists()


@pytest.mark.django_db
def test_add_statement_transaction(client):
    user = User.objects.create_user(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")
    session = client.session
    session['statement_transactions'] = [{
        'Date': '29/11/2024',
        'Description': 'Test Merchant',
        'Type': 'Income',
        'Amount': 100.0,
    }]
    session.save()
    response = client.post("/add_statement_transaction/")
    assert response.status_code == 302
    assert Transaction.objects.filter(user=user, merchant="Test Merchant").exists()


@pytest.mark.django_db
def test_remove_transactions(client):
    user = User.objects.create_user(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")
    session = client.session
    session['statement_transactions'] = [{
        'Date': '29/11/2024',
        'Description': 'Test Merchant',
        'Type': 'Income',
        'Amount': 100.0,
    }]
    session.save()
    response = client.post("/remove_transaction/", {"transaction_index": 0})
    assert response.status_code == 200
    assert len(client.session['statement_transactions']) == 0


# Financial Summary Tests
@pytest.mark.django_db
def test_financial_summary():
    user = User.objects.create_user(username="testuser", password="testpassword")
    Transaction.objects.create(user=user, type="income", amount=500)
    Transaction.objects.create(user=user, type="expense", amount=200)
    summary = FinancialSummary(user)
    assert summary.total_income() == 500
    assert summary.total_expense() == 200
    assert summary.net_balance() == 300


# User Authentication Tests
@pytest.mark.django_db
def test_register_view(client):
    response = client.post("/register/", {
        "username": "newuser",
        "password1": "password",
        "password2": "password",
        "email": "newuser@example.com"
    })
    assert response.status_code == 302  # Redirects after registration
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_custom_login_view(client):
    user = User.objects.create_user(username="testuser", email="testuser@example.com", password="testpassword")
    response = client.post("/login/", {
        "username": "testuser",
        "password": "testpassword",
    })
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


# Dashboard and Report Generation Tests
@pytest.mark.django_db
def test_dashboard_view(client):
    user = User.objects.create_user(username="testuser", password="testpassword")
    Transaction.objects.create(user=user, type="income", amount=500)
    Transaction.objects.create(user=user, type="expense", amount=200)
    client.login(username="testuser", password="testpassword")
    response = client.get("/dashboard/")
    assert response.status_code == 200
    assert b"Total Income: 500" in response.content
    assert b"Total Expense: 200" in response.content
