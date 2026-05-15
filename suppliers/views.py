from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Supplier, SupplierPayment


def supplier_list(request):
    suppliers = Supplier.objects.filter(is_active=True)
    return render(request, 'suppliers/supplier_list.html', {'suppliers': suppliers})


def supplier_add(request):
    if request.method == 'POST':
        Supplier.objects.create(
            name=request.POST.get('name'),
            contact_person=request.POST.get('contact_person', ''),
            phone=request.POST.get('phone'),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            gst_number=request.POST.get('gst_number', ''),
            opening_balance=request.POST.get('opening_balance', 0),
        )
        messages.success(request, 'Supplier added successfully.')
        return redirect('suppliers:supplier_list')
    return render(request, 'suppliers/supplier_add.html')