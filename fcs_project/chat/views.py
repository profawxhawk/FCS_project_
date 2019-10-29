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
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(req_user, other_user)==True:
        a = min(uid,int(pk))
        b = max(int(pk),uid)
        return render(request, 'chat/room.html', {
            'room_name_json': mark_safe(json.dumps(str(a)+"_"+str(b))),
            'username': mark_safe(json.dumps(req_user.username)),
            'username1': mark_safe(json.dumps(other_user.username)),
            'userid': mark_safe(json.dumps(uid)),
            'toid':mark_safe(json.dumps(pk))
        })
    else:
        return redirect(reverse('homepage'))