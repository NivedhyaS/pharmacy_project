from django.urls import path
from . import views

urlpatterns = [
    path('', views.drug_list, name='drug_list'),
    path('add/', views.drug_add, name='drug_add'),
    path('<int:drug_id>/edit/', views.drug_edit, name='drug_edit'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/add/', views.batch_add, name='batch_add'),
    path('batches/drug/<int:drug_id>/', views.get_batches, name='get_batches'),
    path('locator/', views.medicine_locator, name='medicine_locator'),
    path('dashboard/', views.dashboard, name='dashboard'),
]