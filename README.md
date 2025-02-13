
# Expense Tracker

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)


## Description

**Expense Tracker** is a simple yet powerful web application designed to help users manage their finances. Easily record, track, and visualize your income and expenses to make informed financial decisions. With features like budgeting, reports, and export capabilities, it’s the perfect tool for individuals looking to stay on top of their financial health.

## Features

- **User Authentication**: Secure login and registration.
- **Add & Manage Expenses**: Quickly add, edit, or delete expenses.
- **Categorization**: Organize expenses by categories such as groceries, utilities, etc.
- **Budgeting**: Set monthly budgets and monitor your spending.
- **Reports & Analytics**: View detailed reports and charts of your spending.
- **Data Export**: Export data to CSV or PDF for easy record-keeping.
- **Responsive Design**: Mobile-friendly interface.
  


## Screenshots

![Dashboard Screenshot](screenshots/dashboard.png)
_Expense Overview on the Dashboard_

## Installation

### Prerequisites
- [Python 3.x](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [pip](https://pip.pypa.io/en/stable/) for package management.

### Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/expense-tracker.git
    cd expense-tracker
    ```

2. **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**:
    - Create a `.env` file in the project root and set the necessary environment variables like `SECRET_KEY` and `DEBUG`.

5. **Apply migrations**:
    ```bash
    python manage.py migrate
    ```

6. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

7. **Visit**:
    ```
    http://localhost:8000
    ```

## Usage

1. **Sign up** or **log in** to start using the Expense Tracker.
2. **Add expenses** from the dashboard by selecting a category, entering an amount, and adding a description.
3. **View reports** to analyze your spending trends over time.
4. **Export** your expenses in CSV or PDF format for external use.

## Technologies Used

- **Backend**: Django, Python
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (default, can be switched to PostgreSQL or MySQL)
- **Authentication**: Django Authentication

## Contributing

We welcome contributions! Follow these steps to get started:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes and open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries or support, feel free to reach out:

- **Email**: moulish.developer@gmail.com
- **GitHub**: [moulish-dev](https://github.com/moulish-dev)
- **LinkedIn**: [Moulishwaran Balaji](https://www.linkedin.com/in/moulishwaran-balaji/)

