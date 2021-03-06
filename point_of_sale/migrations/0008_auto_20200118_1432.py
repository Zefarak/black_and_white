# Generated by Django 2.2 on 2020-01-18 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0007_auto_20200118_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='extra_value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20),
        ),
        migrations.AddField(
            model_name='orderitemattribute',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
