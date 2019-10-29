from django.shortcuts import render,redirect
from django_otp.decorators import otp_required
from django.urls import reverse
from .forms import GroupCreationform
from .models import Group,Group_user_relation,group_requests
from users.models import premium_users,posts,User
from users.forms import postform
from django.contrib.sessions.models import Session
# Create your views here.
@otp_required
def group_settings(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if Group_user_relation.objects.filter(user_id=req_user.id,group_id=pk):
        group1 = Group.objects.get(pk=pk)
        user1 = req_user
        the_relation = Group_user_relation.objects.filter(group = group1,user = user1)
        number_of_users=len(Group_user_relation.objects.filter(group = group1))
        price=group1.price
        request_sent = group_requests.objects.filter(group=group1)
        desperate_users = []
        for request_i in request_sent:
            desperate_users.append(request_i)
        args1={'no_of_users':number_of_users,'price':price,'group':group1}
        args={'desperate_users':desperate_users,'no_of_users':number_of_users,'price':price,'group':group1}
        if the_relation[0].add_reject_perm == True:
            return render(request, 'groups/groups_settings.html',args)
        if the_relation[0].is_owner == False:
            return render(request, 'groups/groups_settings.html',args1)
        a_rcheck = request.POST.get('add_reject')
        user_check = request.POST.get('user')
        if user_check:
            cur_user=User.objects.get(pk=user_check)
            if Group_user_relation.objects.filter(group = group1,user=cur_user):
                rel=Group_user_relation.objects.filter(group = group1,user=cur_user)[0]
                if a_rcheck:
                    rel.add_reject_perm=True
                else:
                    rel.add_reject_perm=False
                rel.save()
        members_id=Group_user_relation.objects.filter(group = group1).values("user","add_reject_perm").exclude(user=user1)
        members=[]
        add_reject_perm=[]
        for i in members_id:
            members.append(User.objects.get(pk=i['user']))
            add_reject_perm.append(i['add_reject_perm'])
        member_details=zip(members,add_reject_perm)
        args = {'desperate_users':desperate_users,'no_of_users':number_of_users,'price':price,'hid':1,'members':member_details,'group':group1}
        return render(request, 'groups/groups_settings.html',args)
    else:
        return redirect(reverse('homepage'))
@otp_required
def group_wall(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if Group_user_relation.objects.filter(user_id=req_user.id,group_id=pk):
        group=Group.objects.get(pk=pk)
        post = posts.objects.all().order_by('-created')
        if request.method=='GET':
            form = postform()
            args = {
                'form': form, 'posts': post,'group':group
                }
            return render(request, 'groups/wall.html',args)
        else:
            form = postform(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                # post.user=req_user
                post.group = group
                post.posted_by=req_user
                post.text=form.cleaned_data['post']
                post.save()
                form = postform()
                return redirect(reverse('group_wall',kwargs={'pk':pk}))
            args = {'form': form , 'group':group,'posts': post }
            return render(request, 'users/wall.html',args)
    else:
        return redirect(reverse('homepage'))
@otp_required
def groups_u_created(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    groups=Group.objects.filter(owner_id=req_user.id)
    args={'groups':groups}
    return render(request, 'groups/groups_display.html', args)
@otp_required
def create_group(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==True:
        number_of_groups = premium_users.objects.values('number_of_groups').filter(user_id=req_user.id)
        cur_number_of_groups = premium_users.objects.values('current_number_of_groups').filter(user_id=req_user.id)
        temp=(number_of_groups[0]['number_of_groups'])
        ava=cur_number_of_groups[0]['current_number_of_groups']
        if temp>ava:
            if request.method == 'POST':
                form = GroupCreationform(request.POST)
                if form.is_valid():
                    premium_users.objects.filter(user_id=req_user.id).update(current_number_of_groups=ava+1)
                    group=form.save(commit=False)
                    group.owner=req_user
                    group.save()
                    group_user=Group_user_relation(group=group,user=req_user,is_owner=True)
                    print(group_user)
                    group_user.save()
                    return redirect(reverse('show_groups'))

            else:
                form = GroupCreationform()
                args = {'form': form}
                return render(request, 'groups/create_page.html', args)

    return redirect(reverse('show_groups'))

@otp_required
def accept_group_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    request1 = group_requests.objects.get(pk=pk)
    group1 = request1.group
    user1 = request1.user
    group_user1 = Group_user_relation()
    group_user1.group = group1
    group_user1.user = user1
    group_user1.save()
    request1.delete()
    groups = Group.objects.filter(owner_id=req_user.id)
    args={'groups':groups}
    gpk = group1.pk
    return redirect(reverse('group_settings',kwargs={'pk':gpk}))

@otp_required
def reject_group_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    request1 = group_requests.objects.get(pk=pk)
    cur_user = req_user
    requestee = request1.user
    group1 = request1.group
    refund = group1.price
    gpk = group1.pk
    requestee.account_balance += refund
    requestee.save()
    request1.delete()
    groups = Group.objects.filter(owner_id=req_user.id)
    args={'groups':groups}

    return redirect(reverse('group_settings',kwargs={'pk':gpk}))

@otp_required
def groups_you_are_member_of(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    relations_list = Group_user_relation.objects.filter(user = req_user)
    groups = []
    for relation_i in relations_list:
        groups.append(relation_i.group)
    args = {"groups": groups}
    print("\n\n",groups,"\n\n")
    return render(request, 'groups/groups_you_are_member_of.html', args)