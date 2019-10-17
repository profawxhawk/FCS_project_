from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

class User(AbstractUser):
    premium_user=models.BooleanField(default=False)
    account_balance=models.FloatField(default=1000.0)

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    privacy = models.BooleanField(default=False)
    description = models.CharField(max_length=200,default='None')
    city = models.CharField(max_length=200,default='None')
    phone=models.IntegerField(default=0)


def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)