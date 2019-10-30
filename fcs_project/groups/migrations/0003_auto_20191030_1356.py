# Generated by Django 2.2.6 on 2019-10-30 13:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20191029_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='price',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MaxValueValidator(9999999.9)]),
        ),
    ]
