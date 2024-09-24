"""
WSGI config for expense_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # This should point to the directory of the second expense_tracker


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings')

application = get_wsgi_application()

app = application