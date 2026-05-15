from django.db import models

class ShopSettings(models.Model):
    shop_name    = models.CharField(max_length=200, default='PharmaCare')
    address      = models.TextField(blank=True)
    phone        = models.CharField(max_length=15, blank=True)
    email        = models.EmailField(blank=True)
    gst_number   = models.CharField(max_length=20, blank=True)
    logo         = models.ImageField(upload_to='shop/', blank=True, null=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.shop_name

    class Meta:
        verbose_name_plural = 'Shop Settings'