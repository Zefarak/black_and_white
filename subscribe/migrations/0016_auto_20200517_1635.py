# Generated by Django 2.2 on 2020-05-17 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0015_auto_20200517_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('a', 'Μέρες'), ('c', 'Μηνες'), ('b', 'Εβδομαδες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]