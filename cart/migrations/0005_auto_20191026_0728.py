# Generated by Django 2.2.6 on 2019-10-26 04:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_cartitemgifts_cartsubscribe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitemgifts',
            name='cart_related',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gifts', to='cart.Cart'),
        ),
    ]
