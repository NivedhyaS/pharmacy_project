from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.bill_list, name='bill_list'),
    path('new/', views.new_bill, name='new_bill'),
    path('<int:bill_id>/', views.bill_detail, name='bill_detail'),
    path('<int:bill_id>/pdf/', views.bill_pdf, name='bill_pdf'),
    path('<int:bill_id>/cancel/', views.bill_cancel, name='bill_cancel'),

]