# Generated by Django 2.2.4 on 2021-06-09 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20210606_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='product_support_image',
            field=models.BooleanField(default=True, verbose_name='Χρησιμοποιηση εικόνων'),
        ),
    ]
