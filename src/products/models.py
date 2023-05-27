import pathlib

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.urls import reverse
import stripe

from home.env import config

STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY


PROTECTED_MEDIA_ROOT = settings.PROTECTED_MEDIA_ROOT
protected_storage = FileSystemStorage(location=str(PROTECTED_MEDIA_ROOT))


class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    name = models.CharField(max_length=120)
    stripe_product_id = models.CharField(max_length=220, blank=True, null=True)
    handle = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    og_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_changed_timestamp = models.DateTimeField(blank=True, null=True)
    stripe_price = models.IntegerField(default=0)
    stripe_price_id = models.CharField(max_length=220, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.name:
            stripe_product = stripe.Product.create(name=self.name)
            self.stripe_product_id = stripe_product.id
        if not self.stripe_price_id:
            stripe_price = stripe.Price.create(
                product=self.stripe_product_id,
                unit_amount=self.stripe_price,
                currency='usd'
            )
            self.stripe_price_id = stripe_price.id
        if self.price != self.og_price:
            self.og_price = self.price
            self.stripe_price = int(self.price) * 100
            if self.stripe_product_id:
                stripe_price = stripe.Price.create(
                    product=self.stripe_product_id,
                    unit_amount=self.stripe_price,
                    currency='usd'
                )
                self.stripe_price_id = stripe_price.id
            self.price_changed_timestamp = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'handle': self.handle})

    def get_update_url(self):
        return reverse('product_update', kwargs={'handle': self.handle})


def handle_product_attachment_upload(instance, filename):
    return f'products/{instance.product.handle}/attachments/{filename}'


class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(
        upload_to=handle_product_attachment_upload,
        storage=protected_storage
    )
    name = models.CharField(max_length=120, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = pathlib.Path(self.file.name).name
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} - {self.name} attachment ({self.pk})'

    @property
    def display_name(self):
        return self.name or pathlib.Path(self.file.name).name

    def get_download_url(self):
        return reverse('product_attachment_download', kwargs={'handle': self.product.handle, 'pk': self.pk})
