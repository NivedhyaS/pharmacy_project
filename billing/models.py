from django.db import models
from django.contrib.auth.models import User
from drugs.models import Drug, Batch

class Bill(models.Model):
    PAYMENT_MODE = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
    ]

    STATUS = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
    ]

    bill_number     = models.CharField(max_length=20, unique=True)
    patient_name    = models.CharField(max_length=200, blank=True)
    doctor_name     = models.CharField(max_length=200, blank=True)
    prescription_no = models.CharField(max_length=100, blank=True)
    cashier         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment_mode    = models.CharField(max_length=20, choices=PAYMENT_MODE, default='cash')
    status          = models.CharField(max_length=20, choices=STATUS, default='active')
    subtotal        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount        = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancel_reason   = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.bill_number}"

    class Meta:
        ordering = ['-created_at']


class BillItem(models.Model):
    bill            = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    drug            = models.ForeignKey(Drug, on_delete=models.CASCADE)
    batch           = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity        = models.PositiveIntegerField()
    selling_price   = models.DecimalField(max_digits=10, decimal_places=2)
    discount        = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    gst_percent     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cgst            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sgst            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total           = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.drug.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        price_after_discount = self.selling_price * self.quantity
        discount_amount = (price_after_discount * self.discount) / 100
        taxable_amount = price_after_discount - discount_amount
        gst_amount = (taxable_amount * self.gst_percent) / 100
        self.cgst = gst_amount / 2
        self.sgst = gst_amount / 2
        self.total = taxable_amount + gst_amount
        if not self.pk:
            self.batch.quantity -= self.quantity
            self.batch.save()
        super().save(*args, **kwargs)


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('edit', 'Edited'),
        ('cancel', 'Cancelled'),
        ('delete', 'Deleted'),
    ]

    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=100)
    record_id   = models.IntegerField()
    detail      = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name} #{self.record_id}"

    class Meta:
        ordering = ['-timestamp']