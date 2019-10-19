from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from .forms import SignUpForm,EditProfileForm,EditProfileFormextend,postform
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import posts,User, friend_req, posts,map_to_username,premium_users
from friendship.models import Friend, Follow, Block,FriendshipRequest
@login_required
def logout_view(request):
    logout(request)
    return redirect('/') 

@login_required
def options(request):
    return render(request, 'users/options.html')

@login_required
def home(request):
    if request.method=='GET':
        form = postform()
        post = posts.objects.all().order_by('-created')
        users=User.objects.exclude(id=request.user.id)
        pending_requests = friend_req.objects.raw('select to_user_id from friendship_friendshiprequest a where a.from_user_id = '+str(request.user.id)+'  ;',translations={'to_user_id' : 'req_id'})
        sent_req = []
        for obj in pending_requests:
            sent_req.append(obj.req_id)
        unread_req = Friend.objects.unrejected_requests(user=request.user)
        friends = Friend.objects.friends(request.user)
        friend_id = []
        for obj in friends:
            friend_id.append(obj.id)
        pending_id=[]
        for obj in unread_req:
            pending_id.append(obj.from_user_id)
        args = {
            'pending_id':pending_id,'form': form, 'posts': post, 'others':users,'sent':sent_req,'pending':unread_req,'friend_id':friend_id,'friend_iter':friends
        }
        return render(request, 'users/homepage.html',args)
    else:
        form = postform(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.posted_by=request.user
            post.text=form.cleaned_data['post']
            post.save()
            form = postform()
            return redirect(reverse('homepage'))
        args = {'form': form}
        return render(request, 'users/homepage.html',args)

@login_required
def add_friend(request,pk):
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=request.user, to_user=other_user)
    if Friend.objects.are_friends(request.user, other_user) == False and not requests: 
        Friend.objects.add_friend(request.user,other_user,message='Hi! I would like to add you') 
    return redirect(reverse('homepage'))

@login_required
def accept_request(request,pk):
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user)
    if Friend.objects.are_friends(request.user, other_user) == False and requests: 
        friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=request.user.id)
        friend_request.accept()
    return redirect(reverse('homepage'))

@login_required
def reject_request(request,pk):
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user)
    if Friend.objects.are_friends(request.user, other_user) == False and requests: 
        friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=request.user.id)
        friend_request.cancel()
    return redirect(reverse('homepage'))

@login_required
def remove_friend(request,pk):
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(request.user, other_user)==True:
        Friend.objects.remove_friend(request.user, other_user)
    return redirect(reverse('homepage'))


def welcome(request):
    return render(request, 'users/welcome.html')

@login_required
def timeline(request,pk):
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(request.user, other_user) == True:
        post = posts.objects.all().order_by('-created')
        if other_user.userprofile.privacy==False:
            if request.method=='GET':
                form = postform()
                args = {
                    'form': form, 'posts': post, 'friend':other_user
                }
                return render(request, 'users/timeline.html',args)
            else:
                form = postform(request.POST)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.user = other_user
                    post.posted_by=request.user
                    post.text=form.cleaned_data['post']
                    post.save()
                    form = postform()
                    return redirect(reverse("Timeline",kwargs={'pk':other_user.pk}))
        return render(request,'users/timeline.html',{'friend':other_user,'posts': post})
    return redirect(reverse('homepage'))


@login_required
def view_friend(request,pk):
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(request.user, other_user) == True:
        username=other_user.username
        firstname=other_user.first_name
        lastname=other_user.last_name
        description=other_user.userprofile.description
        City=other_user.userprofile.city
        phone=other_user.userprofile.phone
        privacy=other_user.userprofile.privacy
        args={'view':True,'first':firstname,'last':lastname,'desc':description,'city':City,'phone':phone,'privacy':privacy,'username':username,'pk1':other_user.pk}
        return render(request,'users/profilepage.html',args)
    else :
        return redirect(reverse('homepage'))

@login_required
def profilepage(request):
    plan=premium_users.objects.values_list('payment_plan', flat=True).filter(user_id=request.user.id)
    if not plan:
        plan=["None"]
    return render(request,'users/profilepage.html',{'user':request.user,'plan':plan})

@login_required
def editprofile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        form1 = EditProfileFormextend(request.POST, instance=request.user.userprofile)
        if form.is_valid() and form1.is_valid():
            form.save()
            form1.save()
            return redirect(reverse('profilepage'))

    else:
        form = EditProfileForm(instance=request.user)
        form1 = EditProfileFormextend(instance=request.user.userprofile)
        args = {'form': form,'form1': form1}
        return render(request, 'users/edit_profile.html', args)

@login_required
def changepass(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('profilepage'))
        else:
            return redirect(reverse('change_password'))

    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form }
        return render(request, 'users/change_password.html', args)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('homepage'))
    else:
        form = SignUpForm()
    return render(request, 'users/register.html', { 'form' : form })

@login_required
def upgrade(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    plan=[]
    if (request.user.account_balance - 50)>=0:
        plan.append("Silver")
    if (request.user.account_balance - 100)>=0:
        plan.append("Gold")
    if (request.user.account_balance - 150)>=0:
        plan.append("Platinum")
    return render(request, 'users/upgrade.html',{'plans':plan})

@login_required
def silver_plan(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-50) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/silver_plan.html')

@login_required
def gold_plan(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-100) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/gold_plan.html')

@login_required
def platinum_plan(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-150) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/platinum_plan.html')

@login_required
def get_silver(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-50) < 0 :
        return redirect(reverse('upgrade'))
    premium = premium_users()
    premium.user = request.user
    premium.save()
    cur_user = request.user
    prev_balance = cur_user.account_balance
    cur_user.premium_user = True
    cur_user.account_balance = prev_balance - 50
    cur_user.save()
    return render(request, 'users/successful_upgrade.html')

@login_required
def get_gold(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-100) < 0 :
        return redirect(reverse('upgrade'))
    premium = premium_users()
    premium.user = request.user
    premium.payment_plan = 'Gold'
    premium.save()
    cur_user = request.user
    prev_balance = cur_user.account_balance
    cur_user.premium_user = True
    cur_user.account_balance = prev_balance - 100
    cur_user.save()
    return render(request, 'users/successful_upgrade.html')

@login_required
def get_platinum(request):
    if request.user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (request.user.account_balance-150) < 0 :
        return redirect(reverse('upgrade'))
    premium = premium_users()
    premium.user = request.user
    premium.payment_plan = 'platinum'
    premium.save()
    cur_user = request.user
    prev_balance = cur_user.account_balance
    cur_user.premium_user = True
    cur_user.account_balance = prev_balance - 150
    cur_user.save()
    return render(request, 'users/successful_upgrade.html')