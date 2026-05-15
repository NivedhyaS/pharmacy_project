from django.contrib import admin
from .models import Category, Drug, Batch

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'unit', 'rack_number', 'section', 'min_stock', 'is_active']
    search_fields = ['name', 'brand', 'hsn_code']
    list_filter  = ['category', 'unit', 'is_active']


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['drug', 'batch_number', 'expiry_date', 'quantity', 'selling_price', 'is_active']
    search_fields = ['drug__name', 'batch_number']
    list_filter  = ['is_active', 'expiry_date']