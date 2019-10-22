from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
import json

def index(request):
    return render(request, 'chat/index.html', {})

@login_required
def room(request,pk):
    print(int(pk))
    a = min(request.user.id,int(pk))
    b = max(int(pk),request.user.id)
    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(str(a)+str(b))),
        'username': mark_safe(json.dumps(request.user.username)),
        'userid': mark_safe(json.dumps(request.user.id)),
        'toid':mark_safe(json.dumps(pk))
    })