from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from .forms import SignUpForm,EditProfileForm,EditProfileFormextend,postform
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import posts,User
from friendship.models import Friend, Follow, Block
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
        sent_requests=Friend.objects.sent_requests(user=request.user)
        print(post)
        args = {
            'form': form, 'posts': post, 'others':users, 'sent':sent_requests
        }
        return render(request, 'users/homepage.html',args)
    else:
        form = postform(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.text=form.cleaned_data['post']
            post.save()
            form = postform()
            return redirect(reverse('homepage'))
        args = {'form': form}
        return render(request, self.template_name, args)

@login_required
def add_friend(request,pk):
    other_user = User.objects.get(pk=pk)
    Friend.objects.add_friend(request.user,other_user,message='Hi! I would like to add you') 
    return redirect(reverse('homepage'))

    
def welcome(request):
    return render(request, 'users/welcome.html')

@login_required
def profilepage(request):
    return render(request,'users/profilepage.html',{'user':request.user})

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