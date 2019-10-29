from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.urls import reverse
from .forms import SignUpForm,EditProfileForm,get_transaction_amount,EditProfileFormextend,postform
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import posts,User, friend_req, posts,map_to_username,premium_users,transactions,commercial_users,Pages
from friendship.models import Friend, Follow, Block,FriendshipRequest
from django_otp import devices_for_user
from functools import partial
from .forms import SimpleOTPAuthenticationForm,SimpleOTPRegistrationForm,otpform,get_amount,page_form
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.oath import TOTP
from django_otp.util import random_hex
from django_otp.forms import OTPTokenForm
from django_otp import match_token
from django.forms.utils import ErrorList
from django.contrib.auth import views as auth_views
from django.contrib.sessions.models import Session
import sys
import requests
from chat.models import Message
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.html import strip_tags,escape
from django.db.models import Q
from groups.models import Group,Group_user_relation,group_requests


def handler404(request, *args, **argv):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request, *args, **argv):
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response

@login_required
def logout_view(request):
    logout(request)
    return redirect('/') 

@otp_required
def options(request):
    return render(request, 'users/options.html')

@otp_required
def show_groups(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)

    if req_user.premium_user==True:
        number_of_groups = premium_users.objects.values('number_of_groups').filter(user_id=uid)
        cur_number_of_groups = premium_users.objects.values('current_number_of_groups').filter(user_id=uid)
        temp=(number_of_groups[0]['number_of_groups'])
        (number_of_groups)
        ava=cur_number_of_groups[0]['current_number_of_groups']
        if temp > 4: 
            val="Infinite"
        else:
            val=temp-ava
    else:
        val=0
    return render(request, 'users/show_groups.html',{'number':val})

def search_func(query,request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    query = escape(strip_tags(query))
    users=User.objects.filter(Q(username__icontains=query))
    groups=Group.objects.filter(Q(name__icontains=query))
    page=Pages.objects.filter(Q(title__icontains=query))
    friend_list_search=[]
    group_list=[]
    requests_sent = group_requests.objects.filter(user=req_user)
    for i in groups:
        temp=Group_user_relation.objects.filter(group=i,user=req_user)
        if not temp:
            group_list.append(0)
        else:
            group_list.append(1)
    group_final=zip(groups, group_list)
    for i in users:
        if Friend.objects.are_friends(req_user,i)==True:
            friend_list_search.append(i)
    return friend_list_search,group_final,requests_sent,page
    
@otp_required
def home(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    request.session['reverify']=None
    # session = Session.objects.get(session_key=request.session._session_key)
    # uid = session.get_decoded().get('_auth_user_id')
    if request.method=='GET':
        form = postform()
        post = posts.objects.all().order_by('-created')
        users=User.objects.exclude(id=uid)
        pending_requests = friend_req.objects.raw('select to_user_id from friendship_friendshiprequest a where a.from_user_id = '+str(uid)+'  ;',translations={'to_user_id' : 'req_id'})
        sent_req = []
        for obj in pending_requests:
            sent_req.append(obj.req_id)
        unread_req = Friend.objects.unrejected_requests(user=req_user)
        friends = Friend.objects.friends(req_user)
        friend_id = []
        for obj in friends:
            friend_id.append(obj.id)
        pending_id=[]
        for obj in unread_req:
            pending_id.append(obj.from_user_id)
        query = request.GET.get('query')
        messages = Message.objects.filter(to=uid)
        messages_sent = Message.objects.filter(author = uid)
        sent = []
        sent_obj = []
        for obj in messages_sent:
            if obj.to not in sent:
                sent.append(obj.to)
                sent_pk = obj.to
                sent_user = User.objects.get(pk=sent_pk)
                sent_obj.append(sent_user)
        received=[]
        received_obj = []
        for obj in messages:
            if obj.author.premium_user or obj.author.commercial_user:
                if obj.author.pk not in received:
                    received_obj.append(obj.author)
                    received.append(obj.author.pk)
        if query:
            friend_list_search,group_final,requests_sent,page = search_func(query,request)
            requests_sent_to = []
            for tempo in requests_sent:
                requests_sent_to.append(tempo.group)
            args={'friend_search':friend_list_search,'groups_search':group_final,'requests_sent_to':requests_sent_to,'pages':page}
            return render(request, 'users/search_display.html',args)
        args = {
            'pending_id':pending_id,'form': form, 'posts': post, 'others':users,'sent':sent_req,'pending':unread_req,'friend_id':friend_id,'friend_iter':friends,'received':received,'received_obj':received_obj,'sent_obj':sent_obj,'sent_messages':sent,
        }
        return render(request, 'users/homepage.html',args)
    else:
        form = postform(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = req_user
            post.posted_by=req_user
            post.text=form.cleaned_data['post']
            post.save()
            form = postform()
            return redirect(reverse('homepage'))
        args = {'form': form}
        return render(request, 'users/homepage.html',args)

@otp_required
def transaction_occur(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    friends = Friend.objects.friends(req_user)
    friend_id = []
    for obj in friends:
        friend_id.append(obj.id)
    transactions_pending = transactions.objects.filter(to_user=req_user)
    args = {
        'friend_id':friend_id,'friend_iter':friends,'pending':transactions_pending
    }
    return render(request, 'users/transactions.html',args)

@otp_required
def do_transactions(request,pk=None):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.method == 'POST':
        form = get_transaction_amount(request.POST)
        if form.is_valid():
            t_amount = form['amount'].value()
            request.session['amount']=t_amount
            if float(t_amount) > req_user.account_balance or float(t_amount)<0:
                return redirect(reverse('profilepage'))
            return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_transactions','pk':pk}))
           
    else:
        form = get_transaction_amount(instance=req_user)
        args = {'form': form}
        return render(request, 'users/do_transactions.html', args)

@otp_required
def confirm_transactions(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1 and Friend.objects.are_friends(req_user,other_user)==True:
        other_user = User.objects.get(pk=pk)
        transaction_req = transactions()
        transaction_req.from_user = req_user
        transaction_req.to_user = other_user
        transaction_req.amount = float(request.session['amount'])
        req_user.account_balance = req_user.account_balance - float(request.session['amount'])
        request.session['amount']=0
        request.session['reverify']=None
        transaction_req.save()
        req_user.save()
        return redirect(reverse('profilepage'))
    else:
        request.session['reverify']=None
        return redirect(reverse('profilepage'))

@otp_required
def accept_money(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    transaction_req = transactions.objects.get(pk=pk)
    cur_user = req_user
    cur_user.account_balance = cur_user.account_balance + transaction_req.amount
    cur_user.save()
    transaction_req.delete()
    return redirect(reverse('profilepage'))

@otp_required
def confirm_add_money(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1:
        if (req_user.bank_account-float(request.session['amount'])) < 0 :
            request.session['reverify']=None
            return redirect(reverse('upgrade'))
        cur_user = req_user
        prev_balance = cur_user.account_balance
        cur_user.account_balance = prev_balance + float(request.session['amount'])
        cur_user.bank_account = cur_user.bank_account - float(request.session['amount'])
        cur_user.save()
        request.session['reverify']=None
        return redirect(reverse('profilepage'))
    else:
        request.session['reverify']=None
        return redirect(reverse('homepage'))

@otp_required
def add_money(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.method == 'POST':
        form = get_amount(request.POST)
        if form.is_valid():
            t_amount = form['amt'].value()
            if float(t_amount) > req_user.bank_account or float(t_amount) < 0:
                return redirect(reverse('profilepage'))
            request.session['amount']=t_amount
            return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_add_money','pk':1036372758}))
    else:
        form = get_amount(instance=req_user)
        args = {'form': form}
        return render(request, 'users/add_money.html', args)

@otp_required
def reject_money(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    transaction_req = transactions.objects.get(pk=pk)
    cur_user = transaction_req.from_user
    cur_user.account_balance = cur_user.account_balance + transaction_req.amount
    cur_user.save()
    transaction_req.delete()
    return redirect(reverse('profilepage'))

@otp_required
def add_friend(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=req_user, to_user=other_user)
    if Friend.objects.are_friends(req_user, other_user) == False and not requests: 
        Friend.objects.add_friend(req_user,other_user,message='Hi! I would like to add you') 
    return redirect(reverse('homepage'))

@otp_required
def accept_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=req_user)
    if Friend.objects.are_friends(req_user, other_user) == False and requests: 
        friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=uid)
        friend_request.accept()
    return redirect(reverse('homepage'))

@otp_required
def reject_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=req_user)
    if Friend.objects.are_friends(req_user, other_user) == False and requests: 
        friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=uid)
        friend_request.cancel()
    return redirect(reverse('homepage'))

@otp_required
def remove_friend(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(req_user, other_user)==True:
        Friend.objects.remove_friend(req_user, other_user)
    return redirect(reverse('homepage'))


def welcome(request):
    request.session['reverify']=None
    return render(request, 'users/welcome.html')

@otp_required
def timeline(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(req_user, other_user) == True:
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
                    post.group
                    post.user = other_user
                    post.posted_by=req_user
                    post.text=form.cleaned_data['post']
                    post.save()
                    form = postform()
                    return redirect(reverse("Timeline",kwargs={'pk':other_user.pk}))
        return render(request,'users/timeline.html',{'friend':other_user,'posts': post})
    return redirect(reverse('homepage'))


@otp_required
def view_friend(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    other_user = User.objects.get(pk=pk)
    if Friend.objects.are_friends(req_user, other_user) == True:
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

@otp_required
def profilepage(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    plan=premium_users.objects.values_list('payment_plan', flat=True).filter(user_id=uid)
    if not plan:
        plan=["None"]
    return render(request,'users/profilepage.html',{'user':req_user,'plan':plan})

@otp_required
def editprofile(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=req_user)
        form1 = EditProfileFormextend(request.POST, instance=req_user.userprofile)
        if form.is_valid() and form1.is_valid():
            form.save()
            form1.save()
            return redirect(reverse('profilepage'))

    else:
        form = EditProfileForm(instance=req_user)
        form1 = EditProfileFormextend(instance=req_user.userprofile)
        args = {'form': form,'form1': form1}
        return render(request, 'users/edit_profile.html', args)

@otp_required
def changepass(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=req_user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect(reverse('profilepage'))
        else:
            return redirect(reverse('change_password'))

    else:
        form = PasswordChangeForm(user=req_user)
        args = {'form': form }
        return render(request, 'users/change_password.html', args)


@login_required
def otpsetup(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.user.is_verified()==True:
        return redirect(reverse('homepage'))
    totp=TOTPDevice.objects.get(user_id=uid)
    form_cls = partial(SimpleOTPRegistrationForm, req_user)
    temp=totp.config_url.replace("/", "%2F")
    return auth_views.LoginView.as_view(template_name='users/otp_setup.html', authentication_form=form_cls,extra_context={'otpstring':"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl="+str(temp)})(request)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            totp=TOTPDevice()
            totp.user=user
            totp.name=user.username
            totp.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('otpsetup'))
    else:
        form = SignUpForm()
    return render(request, 'users/register.html', { 'form' : form })

@otp_required
def upgrade(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==True:
        return redirect(reverse('profilepage'))
    plan=[]
    if (req_user.account_balance - 50)>=0:
        plan.append("Silver")
    if (req_user.account_balance - 100)>=0:
        plan.append("Gold")
    if (req_user.account_balance - 150)>=0:
        plan.append("Platinum")
    if (req_user.account_balance - 5000)>=0:
        plan.append("Commercial")
    return render(request, 'users/upgrade.html',{'plans':plan})

@otp_required
def silver_plan(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (req_user.account_balance-50) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/silver_plan.html')

@otp_required
def gold_plan(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (req_user.account_balance-100) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/gold_plan.html')

@otp_required
def platinum_plan(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==True:
        return redirect(reverse('profilepage'))
    if (req_user.account_balance-150) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/platinum_plan.html')

@otp_required
def commercial_plan(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.commercial_user==True:
        return redirect(reverse('profilepage'))
    if (req_user.account_balance-5000) < 0 :
        return redirect(reverse('upgrade'))
    return render(request, 'users/commercial_plan.html')

@otp_required
def get_commercial(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1:
        if req_user.commercial_user==True:
            return redirect(reverse('profilepage'))
        if (req_user.account_balance-5000) < 0 :
            return redirect(reverse('upgrade'))
        commercial = commercial_users()
        commercial.user = req_user
        commercial.number_of_groups = 2147483647
        commercial.save()
        cur_user = req_user
        prev_balance = cur_user.account_balance
        cur_user.commercial_user = True
        cur_user.premium_user = False
        cur_user.account_balance = prev_balance - 5000
        cur_user.save()
        return render(request, 'users/successful_upgrade.html')
    else:
        return redirect(reverse('homepage'))

@otp_required
def send_group_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    group_to_join = Group.objects.get(pk=pk)
    cur_user = req_user
    money_with_user = cur_user.account_balance
    money_to_join = group_to_join.price
    if money_to_join > money_with_user:
        return redirect(reverse('show_groups'))
    return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_send_group_request','pk':pk}))

@otp_required
def confirm_send_group_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    group_to_join = Group.objects.get(pk=pk)
    cur_user = req_user
    grp_owner = group_to_join.owner
    request.session['amount']=group_to_join.price
    if request.session['reverify']==1 and request.session['amount']<req_user.account_balance:
        req_user.account_balance = req_user.account_balance - float(request.session['amount'])
        # grp_owner.account_balance += request.session['amount']
        group_request1 = group_requests()
        group_request1.group = group_to_join
        group_request1.user = cur_user
        group_request1.save()
        # grp_owner.save()
        request.session['amount']=0
        request.session['reverify']=None
        req_user.save()
        return redirect(reverse('show_groups'))
    else:
        # print("\nNot Here:(\n")
        request.session['reverify']=None
        return redirect(reverse('show_groups'))

    return redirect(reverse('show_groups'))

@otp_required
def reverify(request,plan,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    request.session['reverify']=None
    if not request.session['reverify']:
        totp=TOTPDevice.objects.get(user_id=uid)
        form = otpform(request.POST)
        temp=totp.config_url.replace("/", "%2F")
        if request.method == 'POST':   
            if form.is_valid():
                otp_token=form.cleaned_data['otp_token']
                result=match_token(req_user,otp_token)
                if not result:
                    errors = form._errors.setdefault("Incorrect OTP", ErrorList())   
                    return render(request,'users/otp_setup.html',{'form':form,'otpstring':"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl="+str(temp),'verification':True,'plan':plan,'pk':pk})
                request.session['reverify']=1
                if plan=="confirm_transactions":
                    return HttpResponseRedirect(reverse(plan,kwargs={'pk':pk}))
                if plan=="confirm_accept_cash_request":
                    return HttpResponseRedirect(reverse(plan,kwargs={'pk':pk}))
                if plan=="confirm_send_group_request":
                    return HttpResponseRedirect(reverse(plan,kwargs={'pk':pk}))
                return HttpResponseRedirect(reverse(plan))
        else:
            return render(request,'users/otp_setup.html',{'form':form,'otpstring':"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl="+str(temp),'verification':True,'plan':plan})
    else:
        return redirect(reverse('homepage'))
@otp_required
def get_silver(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1:
        if req_user.premium_user==True:
            request.session['reverify']=None
            return redirect(reverse('profilepage'))
        if (req_user.account_balance-50) < 0 :
            request.session['reverify']=None
            return redirect(reverse('upgrade'))
        premium = premium_users()
        premium.user = req_user
        premium.payment_plan = 'Silver'
        premium.number_of_groups = 2
        premium.save()
        cur_user = req_user
        prev_balance = cur_user.account_balance
        cur_user.premium_user = True
        cur_user.account_balance = prev_balance - 50
        cur_user.save()
        request.session['reverify']=None
        return render(request, 'users/successful_upgrade.html')
    else:
        return redirect(reverse('homepage'))

@otp_required
def get_gold(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1:
        if req_user.premium_user==True:
            request.session['reverify']=None
            return redirect(reverse('profilepage'))
        if (req_user.account_balance-100) < 0 :
            request.session['reverify']=None
            return redirect(reverse('upgrade'))
        premium = premium_users()
        premium.user = req_user
        premium.payment_plan = 'Gold'
        premium.number_of_groups = 4
        premium.save()
        cur_user = req_user
        prev_balance = cur_user.account_balance
        cur_user.premium_user = True
        cur_user.account_balance = prev_balance - 100
        cur_user.save()
        request.session['reverify']=None
        return render(request, 'users/successful_upgrade.html')
    else:
        return redirect(reverse('homepage'))

@otp_required
def get_platinum(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.session['reverify']==1:
        if req_user.premium_user==True:
            return redirect(reverse('profilepage'))
        if (req_user.account_balance-150) < 0 :
            return redirect(reverse('upgrade'))
        premium = premium_users()
        premium.user = req_user
        premium.payment_plan = 'Platinum'
        premium.number_of_groups = 2147483647
        premium.save()
        cur_user = req_user
        prev_balance = cur_user.account_balance
        cur_user.premium_user = True
        cur_user.account_balance = prev_balance - 150
        cur_user.save()
        return render(request, 'users/successful_upgrade.html')
    else:
        return redirect(reverse('homepage'))
    

@otp_required
def cancel_plan(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.premium_user==False:
        return redirect(reverse('profilepage'))
    premium_users.objects.filter(user=req_user).delete()
    cur_user = req_user
    cur_user.premium_user = False
    cur_user.save()
    return render(request, 'users/cancel_plan.html') 


@otp_required
def accept_group_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    group_to_join = Group.objects.get(pk=pk)
    cur_user = req_user
    group_request1 = group_requests()
    group_request1.user = cur_user
    group_request1.group = group_to_join
    group_request1.save()
    return redirect(reverse('show_groups'))

@otp_required
def request_cash(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if request.method == 'POST':
        form = get_amount(request.POST)
        if form.is_valid():
            t_amount = form['amt'].value()
            if float(t_amount) < 0:
                return redirect(reverse('profilepage'))
            request.session['amount']=t_amount
            money_request = money_requests()
            money_request.amount = t_amount
            money_request.from_user = req_user
            other_user = User.objects.get(pk=pk)
            money_request.to_user = other_user
            money_request.save()
            return redirect(reverse('profilepage'))
    else:
        form = get_amount(instance=req_user)
        args = {'form': form}
        return render(request, 'users/request_cash.html', args)

@otp_required
def accept_cash_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    the_request = money_requests.objects.get(pk=pk)
    request.session['amount']=float(the_request.amount)
    other_user = the_request.from_user
    if Friend.objects.are_friends(req_user,other_user)==False:
        return redirect(reverse('profilepage'))
    if float(the_request.amount) > req_user.account_balance or float(the_request.amount)<0:
        print("\n\nnot un-friends\n\n")
        return redirect(reverse('profilepage'))
    return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_accept_cash_request','pk':pk}))
@otp_required
def confirm_accept_cash_request(request,pk):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    the_request = money_requests.objects.get(pk=pk)
    request.session['amount']=float(the_request.amount)
    other_user = the_request.from_user
    if request.session['reverify']==1 and Friend.objects.are_friends(req_user,other_user)==True and request.session['amount']<req_user.account_balance:
        req_user.account_balance = req_user.account_balance - float(request.session['amount'])
        other_user.account_balance += request.session['amount']
        other_user.save()
        request.session['amount']=0
        request.session['reverify']=None
        req_user.save()
        the_request.delete()
        return redirect(reverse('profilepage'))
    else:
        print("\n\nNot Here:(\n\n")
        request.session['reverify']=None
        return redirect(reverse('profilepage'))

    return redirect(reverse('profilepage'))

@otp_required
def reject_cash_request(request,pk):

    the_request = money_requests.objects.get(pk=pk)
    the_request.delete()
    return redirect(reverse('profilepage'))
@otp_required
def confirm_reject_cash_request(request,pk):
    return redirect(reverse('profilepage'))

@otp_required
def my_pages(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.commercial_user==False:
        return redirect(reverse('profilepage'))
    else:
        lis = Pages.objects.filter(user_id=uid)
        print(lis)
        args = {'lis':lis,}
        return render(request, 'users/my_pages.html', args)

@otp_required
def create_page(request):
    session = Session.objects.get(session_key=request.session._session_key)
    uid = session.get_decoded().get('_auth_user_id')
    req_user = User.objects.get(pk=uid)
    if req_user.commercial_user==False:
        return redirect(reverse('profilepage'))
    else:
        if request.method == 'POST':
        
            # form = page_form(request.POST)
            # if form.is_valid():
            #     form.user = req_user
            #     form.user_id = uid
            #     print(form.user_id)
            #     form.save()
                
            #     return redirect(reverse('profilepage'))
           form = page_form(request.POST,request.FILES)
           if form.is_valid():
               post = form.save(commit=False)
               post.user = req_user
               post.save()
               return redirect(reverse('profilepage'))

        else:
            form = page_form()
            args = {'form': form}
            return render(request, 'users/create_page.html', args)


@otp_required
def show_page(request,pk1):
    page = Pages.objects.filter(pk=pk1)
    args = {'title':page[0].title,'body':page[0].content,'url':page[0].img.url}# pass title and body
    return render(request, 'users/show_page.html', args)


# @otp_required
# def pages(request):
#     if req_user.commercial_user==False:
#         return redirect(reverse('profilepage'))
#     else:
#         args = {}
#         return render(request, 'users/my_pages.html', args)
    # if request.method == 'POST':
    #     form = PasswordChangeForm(data=request.POST, user=req_user)
    #     if form.is_valid():
    #         form.save()
    #         update_session_auth_hash(request, form.user)
    #         return redirect(reverse('profilepage'))
    #     else:
    #         return redirect(reverse('change_password'))

    # else:
    #     form = PasswordChangeForm(user=req_user)
    #     args = {'form': form }
    #     return render(request, 'users/change_password.html', args)