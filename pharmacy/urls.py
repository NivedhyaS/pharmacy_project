from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from drugs import views as drug_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login')),
    path('dashboard/', drug_views.dashboard, name='dashboard'),
    path('drugs/', include('drugs.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('purchases/', include('purchases.urls')),
    path('billing/', include('billing.urls')),
    path('reports/', include('reports.urls')),
    path('accounts/', include('accounts.urls')),
    path('settings/', include('accounts.urls')),

]