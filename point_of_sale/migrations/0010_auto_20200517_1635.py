# Generated by Django 2.2 on 2020-05-17 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('point_of_sale', '0009_auto_20200517_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitemattribute',
            name='attribute',
            field=models.ManyToManyField(null=True, to='catalogue.AttributeTitle'),
        ),
    ]
