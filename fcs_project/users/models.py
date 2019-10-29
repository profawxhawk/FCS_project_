from django.db import models
from groups.models import *
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

class User(AbstractUser):
    premium_user=models.BooleanField(default=False)
    account_balance=models.FloatField(default=1000.0)
    commercial_user=models.BooleanField(default=False)
    bank_account=models.FloatField(default=100000.0)

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    privacy = models.BooleanField(default=False)
    description = models.CharField(max_length=200,default='None')
    city = models.CharField(max_length=200,default='None')
    phone=models.IntegerField(default=0)

class posts(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='owner',default=None,null=True)
    text=models.CharField(max_length=300,default="")
    created = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name='poster',default="")
    group=models.ForeignKey(Group,on_delete=models.CASCADE,related_name='poster',default=None,null=True)

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
    current_number_of_groups = models.IntegerField(default=0)

class commercial_users(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,unique=True)
    number_of_groups = models.IntegerField(default=2)
    current_number_of_groups = models.IntegerField(default=0)

class transactions(models.Model):
    # transaction_id = models.IntegerField(primary_key=True)
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sending_from')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sending_to')
    amount = models.FloatField(default=0.0)

class amount(models.Model):
    amt = models.FloatField(default=0.0)

class money_requests(models.Model):
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='requester')
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='requestee')
    amount = models.FloatField(default=0.0)

class Pages(models.Model):
    #user_id = models.IntegerField(default=1)
    user = models.ForeignKey(User,on_delete=models.CASCADE,unique=False)
    title = models.CharField(max_length=30,default="page")
    # img
    content = models.CharField(max_length=250,default="Welcome to my page!")
    img = models.ImageField(upload_to='images/',default='None')

post_save.connect(create_profile, sender=User)