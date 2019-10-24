from django.shortcuts import render,redirect
from django_otp.decorators import otp_required
from django.urls import reverse
from .forms import GroupCreationform
from .models import Group,Group_user_relation
from users.models import premium_users,posts
from users.forms import postform
# Create your views here.
@otp_required
def group_wall(request,pk):
    if Group_user_relation.objects.filter(user_id=request.user.id,group_id=pk):
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
                # post.user=request.user
                post.group = group
                post.posted_by=request.user
                post.text=form.cleaned_data['post']
                post.save()
                form = postform()
                return redirect(reverse('group_wall',kwargs={'pk':pk}))
            args = {'form': form , 'group':group,'posts': post }
            return render(request, 'users/wall.html',args)
    else:
        return render(reverse('homepage'))
@otp_required
def groups_u_created(request):
    groups=Group.objects.filter(owner_id=request.user.id)
    args={'groups':groups}
    return render(request, 'groups/groups_display.html', args)
@otp_required
def create_group(request):
    if request.user.premium_user==True:
        number_of_groups = premium_users.objects.values('number_of_groups').filter(user_id=request.user.id)
        cur_number_of_groups = premium_users.objects.values('current_number_of_groups').filter(user_id=request.user.id)
        temp=(number_of_groups[0]['number_of_groups'])
        ava=cur_number_of_groups[0]['current_number_of_groups']
        if temp>ava:
            if request.method == 'POST':
                form = GroupCreationform(request.POST)
                if form.is_valid():
                    premium_users.objects.filter(user_id=request.user.id).update(current_number_of_groups=ava+1)
                    group=form.save(commit=False)
                    group.owner=request.user
                    group.save()
                    group_user=Group_user_relation(group=group,user=request.user,is_owner=True)
                    print(group_user)
                    group_user.save()
                    return redirect(reverse('show_groups'))

            else:
                form = GroupCreationform()
                args = {'form': form}
                return render(request, 'groups/create_page.html', args)

    return redirect(reverse('show_groups'))

