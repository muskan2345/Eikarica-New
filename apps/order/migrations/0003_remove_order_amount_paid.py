# Generated by Django 3.0.14 on 2021-08-14 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20210813_1944'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='amount_paid',
        ),
    ]
