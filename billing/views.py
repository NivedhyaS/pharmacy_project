from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Bill, BillItem, AuditLog
from drugs.models import Drug, Batch
from django.db.models import Q
import random


def generate_bill_number():
    return f"BILL-{random.randint(10000000, 99999999):X}"

@login_required
def bill_list(request):
    query   = request.GET.get('q', '')
    status  = request.GET.get('status', '')
    date    = request.GET.get('date', '')

    bills = Bill.objects.all().select_related('cashier')

    if query:
        bills = bills.filter(
            Q(bill_number__icontains=query) |
            Q(patient_name__icontains=query) |
            Q(doctor_name__icontains=query)
        )
    if status:
        bills = bills.filter(status=status)
    if date:
        bills = bills.filter(created_at__date=date)

    return render(request, 'billing/bill_list.html', {
        'bills':  bills,
        'query':  query,
        'status': status,
        'date':   date,
    })
@login_required
def new_bill(request):
    drugs = Drug.objects.filter(is_active=True)

    if request.method == 'POST':
        patient_name = request.POST.get('patient_name', '')
        doctor_name  = request.POST.get('doctor_name', '')
        payment_mode = request.POST.get('payment_mode', 'cash')

        bill = Bill.objects.create(
            bill_number=generate_bill_number(),
            patient_name=patient_name,
            doctor_name=doctor_name,
            payment_mode=payment_mode,
            cashier=request.user,
        )

        drug_ids     = request.POST.getlist('drug')
        batch_ids    = request.POST.getlist('batch')
        quantities   = request.POST.getlist('quantity')
        discounts    = request.POST.getlist('discount')
        gst_percents = request.POST.getlist('gst_percent')

        subtotal  = 0
        gst_total = 0

        from decimal import Decimal

        for i in range(len(drug_ids)):
            if drug_ids[i] and batch_ids[i]:
                try:
                    drug  = Drug.objects.get(id=drug_ids[i])
                    batch = Batch.objects.get(id=batch_ids[i])
                    qty   = int(quantities[i])
                    disc  = Decimal(str(discounts[i] or 0))
                    gst   = Decimal(str(gst_percents[i] or 0))

                    # The BillItem.save() method automatically calculates cgst, sgst, total
                    # and also reduces the batch quantity, so we just need to pass the raw values
                    item = BillItem.objects.create(
                        bill          = bill,
                        drug          = drug,
                        batch         = batch,
                        quantity      = qty,
                        selling_price = batch.selling_price,
                        discount      = disc,
                        gst_percent   = gst,
                    )

                    subtotal  += item.total - item.cgst - item.sgst
                    gst_total += item.cgst + item.sgst

                except Exception as e:
                    messages.error(request, f'Error on item {i+1}: {e}')

        bill.subtotal     = subtotal
        bill.gst_amount   = gst_total
        bill.total_amount = subtotal + gst_total
        bill.save()

        AuditLog.objects.create(
            user=request.user,
            action='create',
            model_name='Bill',
            record_id=bill.id,
            detail=f'Bill {bill.bill_number} created'
        )

        messages.success(request, f'Bill {bill.bill_number} created successfully!')
        return redirect('billing:bill_detail', bill_id=bill.id)

    return render(request, 'billing/new_bill.html', {'drugs': drugs})

@login_required
def bill_detail(request, bill_id):
    bill  = get_object_or_404(Bill, id=bill_id)
    items = bill.items.all().select_related('drug', 'batch')
    return render(request, 'billing/bill_detail.html', {
        'bill': bill,
        'items': items,
    })

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from accounts.models import ShopSettings

def bill_pdf(request, bill_id):
    bill  = get_object_or_404(Bill, id=bill_id)
    items = bill.items.all().select_related('drug', 'batch')
    settings = ShopSettings.objects.first()

    shop_name    = settings.shop_name if settings else 'PharmaCare'
    shop_address = settings.address if settings else 'Kerala'
    shop_phone   = settings.phone if settings else ''
    shop_gst     = settings.gst_number if settings else ''

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bill_{bill.bill_number}.pdf"'

    doc    = SimpleDocTemplate(response, pagesize=A4,
                               rightMargin=15*mm, leftMargin=15*mm,
                               topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    story  = []

    green = colors.HexColor('#1D7A5A')

    # Shop Header
    header_style = ParagraphStyle('header', fontSize=18, textColor=green,
                                   alignment=TA_CENTER, fontName='Helvetica-Bold')
    sub_style    = ParagraphStyle('sub', fontSize=10, alignment=TA_CENTER,
                                   textColor=colors.grey)
    story.append(Paragraph(shop_name, header_style))
    story.append(Paragraph(f"GST No: {shop_gst}", sub_style))
    story.append(Paragraph(f"{shop_address} | Phone: {shop_phone}", sub_style))
    story.append(Spacer(1, 8*mm))

    # Bill Info Table
    bill_info = [
        ['Bill No:', bill.bill_number, 'Date:', bill.created_at.strftime('%d %b %Y %I:%M %p')],
        ['Patient:', bill.patient_name or 'Walk-in', 'Doctor:', bill.doctor_name or '-'],
        ['Payment:', bill.get_payment_mode_display(), 'Cashier:', str(bill.cashier)],
    ]
    info_table = Table(bill_info, colWidths=[30*mm, 70*mm, 30*mm, 50*mm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), green),
        ('TEXTCOLOR', (2,0), (2,-1), green),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 6*mm))

    # Items Table Header
    table_data = [['#', 'Drug', 'Batch', 'Qty', 'Price', 'Disc%', 'GST%', 'Total']]

    for i, item in enumerate(items, 1):
        table_data.append([
            str(i),
            item.drug.name,
            item.batch.batch_number,
            str(item.quantity),
            f'Rs.{item.selling_price}',
            f'{item.discount}%',
            f'{item.gst_percent}%',
            f'Rs.{item.total:.2f}',
        ])

    # Totals
    table_data.append(['', '', '', '', '', '', 'Subtotal', f'Rs.{bill.subtotal:.2f}'])
    table_data.append(['', '', '', '', '', '', 'GST', f'Rs.{bill.gst_amount:.2f}'])
    table_data.append(['', '', '', '', '', '', 'TOTAL', f'Rs.{bill.total_amount:.2f}'])

    col_widths = [10*mm, 45*mm, 25*mm, 12*mm, 22*mm, 14*mm, 14*mm, 22*mm]
    items_table = Table(table_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0,0), (-1,0), green),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('ROWBACKGROUNDS', (0,1), (-1,-4), [colors.white, colors.HexColor('#f0f7f4')]),
        # Total rows
        ('FONTNAME', (0,-3), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), green),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
        ('LINEABOVE', (0,-3), (-1,-3), 1, green),
        ('GRID', (0,0), (-1,-4), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10*mm))

    # Footer
    footer_style = ParagraphStyle('footer', fontSize=9,
                                   alignment=TA_CENTER, textColor=colors.grey)
    story.append(Paragraph("Thank you for your purchase!", footer_style))
    story.append(Paragraph("This is a computer generated invoice.", footer_style))

    doc.build(story)
    return response   

@login_required
def bill_cancel(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    if bill.status == 'cancelled':
        messages.error(request, 'Bill is already cancelled!')
        return redirect('billing:bill_detail', bill_id=bill.id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')

        # Restore stock for each item
        for item in bill.items.all():
            item.batch.quantity += item.quantity
            item.batch.save()

        bill.status        = 'cancelled'
        bill.cancel_reason = reason
        bill.save()

        AuditLog.objects.create(
            user=request.user,
            action='cancel',
            model_name='Bill',
            record_id=bill.id,
            detail=f'Bill {bill.bill_number} cancelled. Reason: {reason}'
        )

        messages.success(request, f'Bill {bill.bill_number} cancelled successfully!')
        return redirect('billing:bill_detail', bill_id=bill.id)

    return render(request, 'billing/bill_cancel.html', {'bill': bill})