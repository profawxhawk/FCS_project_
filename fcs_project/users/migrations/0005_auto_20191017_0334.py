# Generated by Django 2.2.6 on 2019-10-17 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_userprofile_privacy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='city',
            field=models.CharField(default='None', max_length=200),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='description',
            field=models.CharField(default='None', max_length=200),
        ),
    ]