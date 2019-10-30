# Generated by Django 2.2.6 on 2019-10-30 13:56

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='number_of_transactions',
            field=models.IntegerField(default=15),
        ),
        migrations.AlterField(
            model_name='amount',
            name='amt',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MaxValueValidator(9999999.9)]),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='amount',
            field=models.FloatField(default=0.0, validators=[django.core.validators.MaxValueValidator(9999999.9)]),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(9999999999)]),
        ),
    ]