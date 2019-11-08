# Generated by Django 2.2.6 on 2019-11-08 05:57

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0013_auto_20191103_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.date(2019, 11, 8), verbose_name='Ημερομηνία'),
        ),
        migrations.AlterField(
            model_name='ordergift',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifts', to='point_of_sale.Order'),
        ),
    ]