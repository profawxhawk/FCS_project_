from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    premium_user=models.BooleanField(default=False)
    account_balance=models.FloatField(default=1000.0)