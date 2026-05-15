from django.contrib import admin
from .models import Supplier, SupplierPayment

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ['name', 'phone', 'gst_number', 'is_active']
    search_fields = ['name', 'phone', 'gst_number']
    list_filter   = ['is_active']

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display  = ['supplier', 'amount', 'payment_mode', 'payment_date']
    search_fields = ['supplier__name']
    list_filter   = ['payment_mode']