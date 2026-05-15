from django.db import models

class Supplier(models.Model):
    name            = models.CharField(max_length=200)
    contact_person  = models.CharField(max_length=200, blank=True)
    phone           = models.CharField(max_length=15)
    email           = models.EmailField(blank=True)
    address         = models.TextField(blank=True)
    gst_number      = models.CharField(max_length=20, blank=True)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def total_pending(self):
        total_purchased = self.purchases.aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0
        total_paid = self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        return self.opening_balance + total_purchased - total_paid

    class Meta:
        ordering = ['name']


class SupplierPayment(models.Model):
    PAYMENT_MODE = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
    ]

    supplier     = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE, default='cash')
    payment_date = models.DateField()
    note         = models.TextField(blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.supplier.name} - ₹{self.amount} on {self.payment_date}"