from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Transaction

# Register the Transaction model with the admin site
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'type','category','description', 'amount', 'date')
    search_fields = ('category', 'user__username')  # Allows searching by description and username
