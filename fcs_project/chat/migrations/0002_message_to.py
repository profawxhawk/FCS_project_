# Generated by Django 2.2 on 2019-10-21 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='to',
            field=models.IntegerField(default=1),
        ),
    ]