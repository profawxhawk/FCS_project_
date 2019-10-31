from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.utils.safestring import mark_safe
from users.models import User
from django.urls import reverse
import json
from .models import Message
from django.contrib.sessions.models import Session
from django_otp.decorators import otp_required
from friendship.models import Friend, Follow, Block,FriendshipRequest
def index(request):
    try:
        return render(request, 'chat/index.html', {})
    except:
        return redirect(reverse('homepage'))

@otp_required
def room(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        mess = Message.objects.filter(author=other_user,to = request.user.pk)
        print(mess)
        if request.user.commercial_user==True or ( (request.user.premium_user==True or other_user.premium_user==True) and Friend.objects.are_friends(request.user, other_user)==True) or (other_user.commercial_user==True and mess):
            a = min(int(request.user.id),int(pk))
            b = max(int(pk),int(request.user.id))
            return render(request, 'chat/room.html', {
                'room_name_json': mark_safe(json.dumps(str(a)+"_"+str(b))),
                'username': mark_safe(json.dumps(request.user.username)),
                'username1': mark_safe(json.dumps(other_user.username)),
                'userid': mark_safe(json.dumps(request.user.id)),
                'toid':mark_safe(json.dumps(pk))
            })
        else:
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))