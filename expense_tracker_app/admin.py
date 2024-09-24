from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Transaction, Contact_Db

# Register the Transaction model with the admin site
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user','merchant','category','description','type', 'amount', 'date','time','status')
    search_fields = ('category', 'user__username')  # Allows searching by description and username

@admin.register(Contact_Db)
class Contact_DB(admin.ModelAdmin):
    list_display = ('user','subject','message','uploaded_at')