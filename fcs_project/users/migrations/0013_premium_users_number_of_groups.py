# Generated by Django 2.2.6 on 2019-10-23 01:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_transactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='premium_users',
            name='number_of_groups',
            field=models.IntegerField(default=2),
        ),
    ]
