# Generated by Django 3.0.14 on 2021-07-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0013_auto_20210720_1144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor',
            name='idFile',
            field=models.FileField(blank=True, null=True, upload_to='static/uploads'),
        ),
    ]
