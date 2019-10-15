from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from .forms import SignUpForm
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

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