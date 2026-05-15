from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Drug, Batch, Category


@login_required
def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    from billing.models import Bill

    today = timezone.now().date()

    # Drug stats
    total_drugs   = Drug.objects.filter(is_active=True).count()
    total_batches = Batch.objects.filter(is_active=True).count()
    low_stock     = [d for d in Drug.objects.filter(is_active=True) if d.is_low_stock()]

    # Expiry stats
    expiring_soon = Batch.objects.filter(
        is_active=True,
        expiry_date__lte=today + timedelta(days=90),
        expiry_date__gte=today
    ).count()

    expired = Batch.objects.filter(
        is_active=True,
        expiry_date__lt=today
    ).count()

    # Today's billing stats
    today_bills = Bill.objects.filter(
        created_at__date=today,
        status='active'
    )
    today_sales      = sum(b.total_amount for b in today_bills)
    today_bill_count = today_bills.count()

    # This month stats
    month_bills = Bill.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month,
        status='active'
    )
    month_sales = sum(b.total_amount for b in month_bills)

    # Recent bills
    recent_bills = Bill.objects.filter(
        status='active'
    ).select_related('cashier').order_by('-created_at')[:5]

    context = {
        'total_drugs':       total_drugs,
        'total_batches':     total_batches,
        'low_stock_count':   len(low_stock),
        'expiring_soon':     expiring_soon,
        'expired':           expired,
        'today_sales':       today_sales,
        'today_bill_count':  today_bill_count,
        'month_sales':       month_sales,
        'low_stock_drugs':   low_stock[:5],
        'recent_bills':      recent_bills,
    }
    return render(request, 'dashboard.html', context)

@login_required
def drug_list(request):
    query    = request.GET.get('q', '')
    category = request.GET.get('category', '')
    unit     = request.GET.get('unit', '')

    drugs = Drug.objects.filter(is_active=True).select_related('category')

    if query:
        drugs = drugs.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query) |
            Q(hsn_code__icontains=query)
        )
    if category:
        drugs = drugs.filter(category_id=category)
    if unit:
        drugs = drugs.filter(unit=unit)

    categories = Category.objects.all()
    return render(request, 'drugs/drug_list.html', {
        'drugs':      drugs,
        'categories': categories,
        'query':      query,
        'selected_category': category,
        'selected_unit':     unit,
    })

@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'drugs/category_list.html', {'categories': categories})


def batch_list(request):
    batches = Batch.objects.filter(is_active=True).select_related('drug').order_by('expiry_date')
    return render(request, 'drugs/batch_list.html', {'batches': batches})


def medicine_locator(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = Drug.objects.filter(
            Q(name__icontains=query) | Q(brand__icontains=query),
            is_active=True
        ).select_related('category')

    context = {
        'query': query,
        'drugs': results,
    }
    return render(request, 'drugs/locator.html', context)


def get_batches(request, drug_id):
    today = timezone.now().date()
    batches = Batch.objects.filter(
        drug_id=drug_id,
        is_active=True,
        quantity__gt=0,
        expiry_date__gt=today
    ).values('id', 'batch_number', 'expiry_date', 'quantity', 'selling_price')
    return JsonResponse(list(batches), safe=False)

from django.shortcuts import get_object_or_404

@login_required
@user_passes_test(lambda u: u.is_staff)
def drug_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        Drug.objects.create(
            name        = request.POST.get('name'),
            brand       = request.POST.get('brand'),
            composition = request.POST.get('composition'),
            category    = Category.objects.get(id=request.POST.get('category')) if request.POST.get('category') else None,
            unit        = request.POST.get('unit'),
            hsn_code    = request.POST.get('hsn_code'),
            rack_number = request.POST.get('rack_number'),
            row         = request.POST.get('row'),
            shelf       = request.POST.get('shelf'),
            section     = request.POST.get('section'),
            min_stock   = request.POST.get('min_stock') or 10,
        )
        messages.success(request, 'Drug added successfully!')
        return redirect('drug_list')
    return render(request, 'drugs/drug_form.html', {
        'categories': categories,
        'title': 'Add Drug'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def drug_edit(request, drug_id):
    drug       = get_object_or_404(Drug, id=drug_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        drug.name        = request.POST.get('name')
        drug.brand       = request.POST.get('brand')
        drug.composition = request.POST.get('composition')
        drug.category    = Category.objects.get(id=request.POST.get('category')) if request.POST.get('category') else None
        drug.unit        = request.POST.get('unit')
        drug.hsn_code    = request.POST.get('hsn_code')
        drug.rack_number = request.POST.get('rack_number')
        drug.row         = request.POST.get('row')
        drug.shelf       = request.POST.get('shelf')
        drug.section     = request.POST.get('section')
        drug.min_stock   = request.POST.get('min_stock') or 10
        drug.save()
        messages.success(request, 'Drug updated successfully!')
        return redirect('drug_list')
    return render(request, 'drugs/drug_form.html', {
        'categories': categories,
        'drug': drug,
        'title': 'Edit Drug'
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def category_add(request):
    if request.method == 'POST':
        Category.objects.create(
            name          = request.POST.get('name'),
            description   = request.POST.get('description'),
            is_active     = request.POST.get('is_active') == 'on',
        )
        messages.success(request, 'Category added successfully!')
        return redirect('category_list')
    return render(request, 'drugs/category_form.html')

@login_required
@user_passes_test(lambda u: u.is_staff)
def batch_add(request):
    drugs = Drug.objects.filter(is_active=True)
    if request.method == 'POST':
        Batch.objects.create(
            drug             = Drug.objects.get(id=request.POST.get('drug')),
            batch_number     = request.POST.get('batch_number'),
            manufacture_date = request.POST.get('manufacture_date'),
            expiry_date      = request.POST.get('expiry_date'),
            quantity         = request.POST.get('quantity'),
            purchase_price   = request.POST.get('purchase_price'),
            selling_price    = request.POST.get('selling_price'),
        )
        messages.success(request, 'Batch added successfully!')
        return redirect('batch_list')
    return render(request, 'drugs/batch_form.html', {'drugs': drugs})    