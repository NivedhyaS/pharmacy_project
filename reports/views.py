from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from billing.models import Bill, BillItem
from drugs.models import Drug, Batch

@login_required
def reports_home(request):
    return render(request, 'reports/reports_home.html')

@login_required
def daily_sales(request):
    date_str = request.GET.get('date', '')
    if date_str:
        from datetime import datetime
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    bills = Bill.objects.filter(
        created_at__date=selected_date,
        status='active'
    ).select_related('cashier')

    total_sales    = sum(b.total_amount for b in bills)
    total_gst      = sum(b.gst_amount for b in bills)
    total_bills    = bills.count()

    return render(request, 'reports/daily_sales.html', {
        'bills':         bills,
        'total_sales':   total_sales,
        'total_gst':     total_gst,
        'total_bills':   total_bills,
        'selected_date': selected_date,
    })

@login_required
def stock_report(request):
    drugs = Drug.objects.filter(is_active=True).select_related('category')
    low_stock = [d for d in drugs if d.is_low_stock()]
    return render(request, 'reports/stock_report.html', {
        'drugs':     drugs,
        'low_stock': low_stock,
    })

@login_required
def expiry_report(request):
    today = timezone.now().date()
    batches_30 = Batch.objects.filter(
        is_active=True,
        expiry_date__lte=today + timedelta(days=30),
        expiry_date__gte=today
    ).select_related('drug')
    batches_60 = Batch.objects.filter(
        is_active=True,
        expiry_date__lte=today + timedelta(days=60),
        expiry_date__gt=today + timedelta(days=30)
    ).select_related('drug')
    batches_90 = Batch.objects.filter(
        is_active=True,
        expiry_date__lte=today + timedelta(days=90),
        expiry_date__gt=today + timedelta(days=60)
    ).select_related('drug')
    expired = Batch.objects.filter(
        is_active=True,
        expiry_date__lt=today
    ).select_related('drug')

    return render(request, 'reports/expiry_report.html', {
        'batches_30': batches_30,
        'batches_60': batches_60,
        'batches_90': batches_90,
        'expired':    expired,
    })