# Generated by Django 2.2.6 on 2019-11-24 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscribe', '0004_auto_20191124_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscribe',
            name='category',
            field=models.CharField(choices=[('b', 'Εβδομαδες'), ('a', 'Μέρες'), ('c', 'Μηνες')], max_length=1, verbose_name='Κατηγορία'),
        ),
    ]