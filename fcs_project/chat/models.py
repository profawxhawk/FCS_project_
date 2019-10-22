from django.contrib.auth import get_user_model
from django.db import models
from itertools import chain

User = get_user_model()

class Message(models.Model):
    author = models.ForeignKey(User, related_name='author_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    to = models.IntegerField(default=1)

    def __str__(self):
        return self.author.username

    def last_10_messages(name,too):
        lis1 = Message.objects.filter(author=name,to=too)
        lis2 = Message.objects.filter(author=too,to=name)
        #result = chain(lis1,lis2)
        result = sorted(chain(lis1,lis2),key=lambda instance:instance.timestamp)
        print(result)
        #lis1.append(lis2)
        return result