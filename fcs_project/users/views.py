from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from .forms import SignUpForm,EditProfileForm,EditProfileFormextend
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
@login_required
def logout_view(request):
    logout(request)
    return redirect('/') 
@login_required
def options(request):
    return render(request, 'users/options.html')

def home(request):
    return render(request, 'users/welcome.html')

def welcome(request):
    return render(request, 'users/home.html')
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


def changepass(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(reverse('profilepage'))

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