# Generated by Django 2.2.6 on 2019-11-08 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0015_auto_20191108_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('c', 'Μηνες'), ('a', 'Μέρες'), ('b', 'Εβδομαδες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]