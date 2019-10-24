from django.db import models
# Create your models here.

class Group(models.Model):
    owner = models.ForeignKey('users.User',on_delete=models.CASCADE)
    name=models.CharField(max_length=200,default='None')
    price=models.FloatField(default=0.0)
    privacy = models.BooleanField(default=False)

class Group_user_relation(models.Model):
    group=models.ForeignKey(Group,on_delete=models.CASCADE)
    user=models.ForeignKey('users.User',on_delete=models.CASCADE)
    is_owner=models.BooleanField(default=False)
    


