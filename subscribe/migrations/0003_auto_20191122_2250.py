# Generated by Django 2.2.6 on 2019-11-22 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0002_auto_20191121_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('c', 'Μηνες'), ('a', 'Μέρες'), ('b', 'Εβδομαδες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]
