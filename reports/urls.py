from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('daily/', views.daily_sales, name='daily_sales'),
    path('stock/', views.stock_report, name='stock_report'),
    path('expiry/', views.expiry_report, name='expiry_report'),
]