# Generated by Django 2.2.6 on 2019-11-21 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('c', 'Μηνες'), ('b', 'Εβδομαδες'), ('a', 'Μέρες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]
