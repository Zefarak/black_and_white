# Generated by Django 2.2 on 2019-10-29 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0007_auto_20191027_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('c', 'Μηνες'), ('b', 'Εβδομαδες'), ('a', 'Μέρες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]