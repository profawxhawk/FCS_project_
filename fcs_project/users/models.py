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

class posts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='owner')
    text=models.CharField(max_length=300,default="")
    created = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='poster',default="")

class friend_req(models.Model):
    req_id = models.IntegerField(primary_key=True)

class map_to_username(models.Model):
    user_id = models.IntegerField(primary_key=True)
    uname = models.CharField(max_length=300,default="")
    
def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])
       
class premium_users(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,unique=True)
    payment_plan = models.CharField(max_length=30,default="Silver")
    number_of_groups = models.IntegerField(default=2)

class transactions(models.Model):
    # transaction_id = models.IntegerField(primary_key=True)
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sending_from')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sending_to')
    amount = models.FloatField(default=0.0)

post_save.connect(create_profile, sender=User)