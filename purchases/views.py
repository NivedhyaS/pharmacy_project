from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Purchase, PurchaseItem
from suppliers.models import Supplier
from drugs.models import Drug, Batch


def purchase_list(request):
    purchases = Purchase.objects.select_related('supplier').all()
    return render(request, 'purchases/purchase_list.html', {'purchases': purchases})


def purchase_add(request):
    suppliers = Supplier.objects.filter(is_active=True)
    drugs = Drug.objects.filter(is_active=True)

    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        invoice_number = request.POST.get('invoice_number')
        invoice_date = request.POST.get('invoice_date')
        note = request.POST.get('note', '')

        purchase = Purchase.objects.create(
            supplier_id=supplier_id,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            note=note,
        )

        drug_ids = request.POST.getlist('drug_id')
        total = 0
        for i, drug_id in enumerate(drug_ids):
            qty = int(request.POST.getlist('quantity')[i])
            purchase_price = float(request.POST.getlist('purchase_price')[i])
            selling_price = float(request.POST.getlist('selling_price')[i])
            batch_number = request.POST.getlist('batch_number')[i]
            manufacture_date = request.POST.getlist('manufacture_date')[i]
            expiry_date = request.POST.getlist('expiry_date')[i]
            gst_percent = float(request.POST.getlist('gst_percent')[i] or 0)

            PurchaseItem.objects.create(
                purchase=purchase,
                drug_id=drug_id,
                batch_number=batch_number,
                manufacture_date=manufacture_date,
                expiry_date=expiry_date,
                quantity=qty,
                purchase_price=purchase_price,
                selling_price=selling_price,
                gst_percent=gst_percent,
            )

            # Create or update batch in inventory
            Batch.objects.create(
                drug_id=drug_id,
                batch_number=batch_number,
                manufacture_date=manufacture_date,
                expiry_date=expiry_date,
                quantity=qty,
                purchase_price=purchase_price,
                selling_price=selling_price,
            )

            total += qty * purchase_price

        purchase.total_amount = total
        purchase.save()

        messages.success(request, f'Purchase #{invoice_number} added successfully.')
        return redirect('purchases:purchase_list')

    context = {'suppliers': suppliers, 'drugs': drugs}
    return render(request, 'purchases/purchase_add.html', context)