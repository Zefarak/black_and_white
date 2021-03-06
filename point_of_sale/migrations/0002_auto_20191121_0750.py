# Generated by Django 2.2.6 on 2019-11-21 05:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='favorite',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='date_expired',
            field=models.DateField(default=datetime.date(2019, 11, 21), verbose_name='Ημερομηνία'),
        ),
    ]
