from django.db import models
from suppliers.models import Supplier
from drugs.models import Drug, Batch


class Purchase(models.Model):
    supplier       = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='purchases')
    invoice_number = models.CharField(max_length=100)
    invoice_date   = models.DateField()
    total_amount   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note           = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Purchase #{self.invoice_number}'

    class Meta:
        ordering = ['-invoice_date']


class PurchaseItem(models.Model):
    purchase         = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    drug             = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='purchase_items')
    batch_number     = models.CharField(max_length=100)
    manufacture_date = models.DateField()
    expiry_date      = models.DateField()
    quantity         = models.PositiveIntegerField()
    purchase_price   = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price    = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percent      = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.drug.name} - {self.quantity} units'
