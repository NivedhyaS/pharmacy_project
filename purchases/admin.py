from django.contrib import admin
from .models import Purchase, PurchaseItem

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'invoice_date', 'total_amount', 'created_at']
    search_fields = ['invoice_number']
    list_filter = ['invoice_date', 'created_at']
    inlines = [PurchaseItemInline]