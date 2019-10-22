from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.utils.safestring import mark_safe
from users.models import User
from django.urls import reverse
import json
from django_otp.decorators import otp_required
from friendship.models import Friend, Follow, Block,FriendshipRequest
def index(request):
    return render(request, 'chat/index.html', {})

@otp_required
def room(request,pk):
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(request.user, other_user)==True:
        a = min(request.user.id,int(pk))
        b = max(int(pk),request.user.id)
        return render(request, 'chat/room.html', {
            'room_name_json': mark_safe(json.dumps(str(a)+str(b))),
            'username': mark_safe(json.dumps(request.user.username)),
            'username1': mark_safe(json.dumps(other_user.username)),
            'userid': mark_safe(json.dumps(request.user.id)),
            'toid':mark_safe(json.dumps(pk))
        })
    else:
        return redirect(reverse('homepage'))