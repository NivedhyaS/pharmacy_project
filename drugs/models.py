from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Drug(models.Model):
    UNIT_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('drops', 'Drops'),
        ('cream', 'Cream'),
        ('others', 'Others'),
    ]

    name          = models.CharField(max_length=200)
    brand         = models.CharField(max_length=200, blank=True)
    composition   = models.TextField(blank=True)
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unit          = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablet')
    hsn_code      = models.CharField(max_length=20, blank=True)
    rack_number   = models.CharField(max_length=20, blank=True)
    row           = models.CharField(max_length=20, blank=True)
    shelf         = models.CharField(max_length=20, blank=True)
    section       = models.CharField(max_length=100, blank=True)
    min_stock     = models.PositiveIntegerField(default=10)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.brand}"

    def current_stock(self):
        from django.utils import timezone
        return self.batches.filter(
            is_active=True,
            expiry_date__gte=timezone.now().date()
        ).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0

    def is_low_stock(self):
        return self.current_stock() <= self.min_stock


class Batch(models.Model):
    drug            = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='batches')
    batch_number    = models.CharField(max_length=100)
    manufacture_date = models.DateField()
    expiry_date     = models.DateField()
    quantity        = models.PositiveIntegerField(default=0)
    purchase_price  = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price   = models.DecimalField(max_digits=10, decimal_places=2)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.drug.name} | Batch: {self.batch_number} | Exp: {self.expiry_date}"

    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()

    class Meta:
        ordering = ['expiry_date']
        verbose_name_plural = "Batches"
