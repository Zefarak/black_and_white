# Generated by Django 2.2.6 on 2020-05-17 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_attributetitle_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributeclass',
            name='products',
            field=models.ManyToManyField(to='catalogue.Product'),
        ),
    ]
