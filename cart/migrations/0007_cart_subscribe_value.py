# Generated by Django 2.2.6 on 2019-10-27 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0006_cartsubscribediscount'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='subscribe_value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Κοστος Συνδρομης'),
        ),
    ]
