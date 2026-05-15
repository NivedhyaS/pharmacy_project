from django.contrib import admin
from .models import Bill, BillItem, AuditLog

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display  = ['bill_number', 'patient_name', 'cashier', 'payment_mode', 'total_amount', 'status', 'created_at']
    search_fields = ['bill_number', 'patient_name', 'doctor_name']
    list_filter   = ['status', 'payment_mode', 'created_at']
    inlines       = [BillItemInline]

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ['user', 'action', 'model_name', 'record_id', 'timestamp']
    search_fields = ['user__username', 'model_name']
    list_filter   = ['action']