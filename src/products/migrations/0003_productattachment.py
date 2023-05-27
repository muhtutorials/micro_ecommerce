# Generated by Django 4.2.1 on 2023-05-22 15:56

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import products.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0002_product_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='D:\\code\\micro_ecommerce\\src\\protected_media'), upload_to=products.models.handle_product_attachment_upload)),
                ('is_free', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]