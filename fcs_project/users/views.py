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
from binascii import unhexlify
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
    try:
        logout(request)
        return redirect('/')
    except:
        return redirect(reverse('homepage'))

@otp_required
def options(request):
    try:
        return render(request, 'users/options.html')
    except:
        return redirect(reverse('homepage')

@otp_required
def show_groups(request):
    try:
        if request.user.premium_user==True:
            number_of_groups = premium_users.objects.values('number_of_groups').filter(user_id=request.user.id)
            cur_number_of_groups = premium_users.objects.values('current_number_of_groups').filter(user_id=request.user.id)
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
    except:
        return redirect(reverse('homepage'))
@otp_required
def search_func(query,request):
    try:
        query = escape(strip_tags(query))
        users=User.objects.filter(Q(username__icontains=query))
        groups=Group.objects.filter(Q(name__icontains=query))
        page=Pages.objects.filter(Q(title__icontains=query))
        friend_list_search=[]
        group_list=[]
        requests_sent = group_requests.objects.filter(user=request.user)
        for i in groups:
            temp=Group_user_relation.objects.filter(group=i,user=request.user)
            if not temp:
                group_list.append(0)
            else:
                group_list.append(1)
        group_final=zip(groups, group_list)
        for i in users:
            if Friend.objects.are_friends(request.user,i)==True:
                friend_list_search.append(i)
        return friend_list_search,group_final,requests_sent,page
    except:
        return redirect(reverse('homepage'))
    
@otp_required
@otp_required
def home(request):
    try:
        request.session['reverify']=None
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
            query = request.GET.get('query')
            messages = Message.objects.filter(to=request.user.id)
            messages_sent = Message.objects.filter(author = request.user.id)
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
                post.user = request.user
                post.posted_by=request.user
                post.text=form.cleaned_data['post']
                post.save()
                form = postform()
                return redirect(reverse('homepage'))
            args = {'form': form}
            return render(request, 'users/homepage.html',args)
    except:
        return redirect(reverse('homepage'))

@otp_required
@otp_required
def transaction_occur(request):
    try:
        friends = Friend.objects.friends(request.user)
        friend_id = []
        for obj in friends:
            friend_id.append(obj.id)
        transactions_pending = transactions.objects.filter(to_user=request.user)
        args = {
            'friend_id':friend_id,'friend_iter':friends,'pending':transactions_pending
        }
        return render(request, 'users/transactions.html',args)
    except:
        return redirect(reverse('homepage'))
@otp_required
def do_transactions(request,pk=None):
    try:
        if request.method == 'POST':
            form = get_transaction_amount(request.POST)
            if form.is_valid():
                t_amount = form['amount'].value()
                request.session['amount']=t_amount
                if float(t_amount) > request.user.account_balance or float(t_amount)<0 or request.user.number_of_transactions<0:
                    return redirect(reverse('profilepage'))
                return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_transactions','pk':pk}))
               
        else:
            form = get_transaction_amount(instance=request.user)
            args = {'form': form}
            return render(request, 'users/do_transactions.html', args)
    except:
        return redirect(reverse('homepage'))

@otp_required
def confirm_transactions(request,pk):
    try:
        user2 = User.objects.get(pk=request.user.id)
        try:
            other_user2 = User.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        if request.session['reverify']==1 and Friend.objects.are_friends(user2,other_user2)==True and user2.account_balance>=request.session['amount']:
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                try:
                    other_user = User.objects.select_for_update().get(pk=pk)
                except:
                    return redirect(reverse('homepage'))
                transaction_req = transactions()
                transaction_req.from_user = user1
                transaction_req.to_user = other_user
                transaction_req.amount = float(request.session['amount'])
                user1.account_balance = user1.account_balance - float(request.session['amount'])
                request.session['amount']=0
                request.session['reverify']=None
                transaction_req.save()
                user1.save()
            return redirect(reverse('profilepage'))
        else:
            request.session['reverify']=None
            return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage')) 

@otp_required
def accept_money(request,pk):
    try:
        try:
            transaction_req = transactions.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        cur_user = request.user
        cur_user.number_of_transactions=cur_user.number_of_transactions-1
        other_user.number_of_transactions=other_user.number_of_transactions-1
        cur_user.account_balance = cur_user.account_balance + transaction_req.amount
        cur_user.save()
        transaction_req.delete()
        return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def confirm_add_money(request):
    try:
        if request.session['reverify']==1:
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                if (user1.bank_account-float(request.session['amount'])) < 0 :
                    request.session['reverify']=None
                    return redirect(reverse('upgrade'))
                prev_balance = user1.account_balance
                user1.account_balance = prev_balance + float(request.session['amount'])
                user1.bank_account = user1.bank_account - float(request.session['amount'])
                user1.save()
                request.session['reverify']=None
            return redirect(reverse('profilepage'))
        else:
            request.session['reverify']=None
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def add_money(request):
    try:
        if request.method == 'POST':
            form = get_amount(request.POST)
            if form.is_valid():
                t_amount = form['amt'].value()
                if float(t_amount) > request.user.bank_account or float(t_amount) < 0:
                    return redirect(reverse('profilepage'))
                request.session['amount']=t_amount
                return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_add_money','pk':1036372758}))
        else:
            form = get_amount(instance=request.user)
            args = {'form': form}
            return render(request, 'users/add_money.html', args)
    except:
        return redirect(reverse('homepage'))

 @otp_required
def reject_money(request,pk):
    try:  
        try:
            transaction_req = transactions.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        cur_user = transaction_req.from_user
        cur_user.account_balance = cur_user.account_balance + transaction_req.amount
        cur_user.save()
        transaction_req.delete()
        return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage'))       

@otp_required
def add_friend(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            # print("\n\nsolved broski\n\n")
            return redirect(reverse('homepage'))
        requests=FriendshipRequest.objects.filter(from_user=request.user, to_user=other_user)
        if Friend.objects.are_friends(request.user, other_user) == False and not requests: 
            Friend.objects.add_friend(request.user,other_user,message='Hi! I would like to add you') 
        return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def accept_request(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            # print("\n\nsolved broski\n\n")
            return redirect(reverse('homepage'))
        requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user)
        if Friend.objects.are_friends(request.user, other_user) == False and requests: 
            friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=request.user.id)
            friend_request.accept()
        return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def reject_request(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        requests=FriendshipRequest.objects.filter(from_user=other_user, to_user=request.user)
        if Friend.objects.are_friends(request.user, other_user) == False and requests: 
            friend_request = FriendshipRequest.objects.get(from_user=pk,to_user=request.user.id)
            friend_request.cancel()
        return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def remove_friend(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            # print("\n\nsolved broski\n\n")
            return redirect(reverse('homepage'))
        if Friend.objects.are_friends(request.user, other_user)==True:
            Friend.objects.remove_friend(request.user, other_user)
        return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

def welcome(request):
    try:
        request.session['reverify']=None
        return render(request, 'users/welcome.html')
    except:
        return redirect(reverse('homepage'))


@otp_required
def timeline(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            # print("\n\nsolved broski\n\n")
            return redirect(reverse('homepage'))
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
                        post.group
                        post.user = other_user
                        post.posted_by=request.user
                        post.text=form.cleaned_data['post']
                        post.save()
                        form = postform()
                        return redirect(reverse("Timeline",kwargs={'pk':other_user.pk}))
            return render(request,'users/timeline.html',{'friend':other_user,'posts': post})
        return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))


@otp_required
def view_friend(request,pk):
    try:
        try:
            other_user = User.objects.get(pk=pk)
        except:
            # print("\n\nsolved broski\n\n")
            return redirect(reverse('homepage'))
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
    except:
        return redirect(reverse('homepage'))

@otp_required
def profilepage(request):
    try:
        plan=premium_users.objects.values_list('payment_plan', flat=True).filter(user_id=request.user.id)
        if not plan:
            plan=["None"]
        return render(request,'users/profilepage.html',{'user':request.user,'plan':plan})
    except:
        return redirect(reverse('homepage'))

@otp_required
def editprofile(request):
    try:
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
    except:
        return redirect(reverse('homepage'))

@otp_required
def changepass(request):
    try:
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
    except:
        return redirect(reverse('homepage'))


@login_required
def otpsetup(request):
    try:
        if request.user.is_verified()==True:
            return redirect(reverse('homepage'))
        totp=TOTPDevice.objects.get(user_id=request.user.id)
        form_cls = partial(SimpleOTPRegistrationForm, request.user)
        temp=totp.config_url.replace("/", "%2F")
        return auth_views.LoginView.as_view(template_name='users/otp_setup.html', authentication_form=form_cls,extra_context={'otpstring':"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl="+str(temp)})(request)
    except:
        return redirect(reverse('homepage'))

def signup(request):
    try:
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
    except:
        return redirect(reverse('homepage'))

@otp_required
def upgrade(request):
    try:
        if request.user.premium_user==True:
            return redirect(reverse('profilepage'))
        plan=[]
        if (request.user.account_balance - 50)>=0:
            plan.append("Silver")
        if (request.user.account_balance - 100)>=0:
            plan.append("Gold")
        if (request.user.account_balance - 150)>=0:
            plan.append("Platinum")
        if (request.user.account_balance - 5000)>=0:
            plan.append("Commercial")
        return render(request, 'users/upgrade.html',{'plans':plan})
    except:
        return redirect(reverse('homepage'))
@otp_required
def silver_plan(request):
    try:
        
        if request.user.premium_user==True or request.user.commercial_user==True:
            return redirect(reverse('profilepage'))
        if (request.user.account_balance-50) < 0 :
            return redirect(reverse('upgrade'))
        return render(request, 'users/silver_plan.html')
    except:
        return redirect(reverse('homepage'))

@otp_required
def gold_plan(request):
    try:
        
        if request.user.premium_user==True or request.user.commercial_user==True:
            return redirect(reverse('profilepage'))
        if (request.user.account_balance-100) < 0 :
            return redirect(reverse('upgrade'))
        return render(request, 'users/gold_plan.html')
    except:
        return redirect(reverse('homepage'))

@otp_required
def platinum_plan(request):
    try:
        if request.user.premium_user==True or request.user.commercial_user==True:
            return redirect(reverse('profilepage'))
        if (request.user.account_balance-150) < 0 :
            return redirect(reverse('upgrade'))
        return render(request, 'users/platinum_plan.html')
    except:
        return redirect(reverse('homepage'))

@otp_required
def commercial_plan(request):
    try:
        if request.user.commercial_user==True or request.user.premium_user==True:
            return redirect(reverse('profilepage'))
        if (request.user.account_balance-5000) < 0 :
            return redirect(reverse('upgrade'))
        return render(request, 'users/commercial_plan.html')
    except:
        return redirect(reverse('homepage'))

@otp_required
def get_commercial(request):
    try:
        if request.session['reverify']==1:
            if request.user.commercial_user==True or request.user.premium_user==True:
                return redirect(reverse('profilepage'))
            if (request.user.account_balance-5000) < 0:
                return redirect(reverse('upgrade'))
            commercial = commercial_users()
            commercial.user = request.user
            commercial.number_of_groups = 2147483647
            commercial.save()
            cur_user = request.user
            prev_balance = cur_user.account_balance
            cur_user.commercial_user = True
            cur_user.premium_user = False
            cur_user.account_balance = prev_balance - 5000
            cur_user.number_of_transactions = 2147483647
            cur_user.save()
            return render(request, 'users/successful_upgrade.html')
        else:
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def send_group_request(request,pk):
    try:
        try:
            group_to_join = Group.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        cur_user = request.user
        money_with_user = cur_user.account_balance
        money_to_join = group_to_join.price
        if money_to_join > money_with_user:
            return redirect(reverse('show_groups'))
        return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_send_group_request','pk':pk}))
    except:
        return redirect(reverse('homepage'))

@otp_required
def confirm_send_group_request(request,pk):
    try:
        user2 = User.objects.get(pk=request.user.id)
        request.session['amount']=group_to_join.price
        if request.session['reverify']==1 and request.session['amount']<user2.account_balance:
            with transaction.atomic():
                try:
                    group_to_join = Group.objects.select_for_update().get(pk=pk)
                except:
                    return redirect(reverse('homepage'))
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                user1.account_balance = user1.account_balance - float(request.session['amount'])
                # grp_owner.account_balance += request.session['amount']
                group_request1 = group_requests()
                group_request1.group = group_to_join
                group_request1.user = cur_user
                group_request1.save()
                # grp_owner.save()
                request.session['amount']=0
                request.session['reverify']=None
                user1.save()
            return redirect(reverse('show_groups'))
        else:
            # print("\nNot Here:(\n")
            request.session['reverify']=None
            return redirect(reverse('show_groups'))

        return redirect(reverse('show_groups'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def reverify(request,plan,pk):
    try:
        request.session['reverify']=None
        if not request.session['reverify']:
            totp=TOTPDevice.objects.get(user_id=request.user.id)
            form = otpform(request.POST)
            temp=totp.config_url.replace("/", "%2F")
            if request.method == 'POST':   
                if form.is_valid():
                    otp_token=form.cleaned_data['otp_token']
                    result=match_token(request.user,otp_token)
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
    except:
        return redirect(reverse('homepage'))
        @otp_required
def get_silver(request):
    try:
        user2 = User.objects.get(pk=request.user.id)
        if request.session['reverify']==1:
            with transaction.atomic():
                if user2.premium_user==True or user2.commercial_user==True:
                    request.session['reverify']=None
                    return redirect(reverse('profilepage'))
            if (user2.account_balance-50) < 0 :
                request.session['reverify']=None
                return redirect(reverse('upgrade'))
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                premium = premium_users()
                premium.user = user1
                premium.payment_plan = 'Silver'
                premium.number_of_groups = 2
                premium.save()
                cur_user = user1
                prev_balance = cur_user.account_balance
                cur_user.premium_user = True
                cur_user.account_balance = prev_balance - 50
                cur_user.number_of_transactions = 15
                cur_user.save()
                request.session['reverify']=None
            return render(request, 'users/successful_upgrade.html')
        else:
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def get_gold(request):
    try:
        
        user2 = User.objects.get(pk=request.user.id)
        if request.session['reverify']==1:
            if user2.premium_user==True or user2.commercial_user==True:
                request.session['reverify']=None
                return redirect(reverse('profilepage'))
            if (user2.account_balance-100) < 0 :
                request.session['reverify']=None
                return redirect(reverse('upgrade'))
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                premium = premium_users()
                premium.user = user1
                premium.payment_plan = 'Gold'
                premium.number_of_groups = 4
                premium.save()
                cur_user = user1
                prev_balance = cur_user.account_balance
                cur_user.premium_user = True
                cur_user.account_balance = prev_balance - 100
                cur_user.number_of_transactions = 30
                cur_user.save()
                request.session['reverify']=None
            return render(request, 'users/successful_upgrade.html')
        else:
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def get_platinum(request):
    try:
        user2 = User.objects.get(pk=request.user.id)
        if request.session['reverify']==1:
            if user2.premium_user==True or user2.commercial_user==True:
                return redirect(reverse('profilepage'))
            if (user2.account_balance-150) < 0 :
                return redirect(reverse('upgrade'))
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=request.user.id)
                premium = premium_users()
                premium.user = user1
                premium.payment_plan = 'Platinum'
                premium.number_of_groups = 2147483647
                premium.save()
                cur_user = user1
                prev_balance = cur_user.account_balance
                cur_user.premium_user = True
                cur_user.account_balance = prev_balance - 150
                cur_user.number_of_transactions = 2147483647
                cur_user.save()
            return render(request, 'users/successful_upgrade.html')
        else:
            return redirect(reverse('homepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def cancel_plan(request):
    try:
        if request.user.premium_user==False and request.user.commercial_user==False:
            return redirect(reverse('profilepage'))
        if request.user.premium_user==True:
            premium_users.objects.filter(user=request.user).delete()
            cur_user = request.user
            cur_user.premium_user = False
            cur_user.number_of_transactions = 15
            cur_user.save()
        else:
            commercial_users.objects.filter(user=request.user).delete()
            cur_user = request.user
            cur_user.commercial_user = False
            cur_user.number_of_transactions = 15
            cur_user.save()
        return render(request, 'users/cancel_plan.html') 
    except:
        return redirect(reverse('homepage'))

@otp_required
def accept_group_request(request,pk):
    try:
        try:
            group_to_join = Group.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        cur_user = request.user
        group_request1 = group_requests()
        group_request1.user = cur_user
        group_request1.group = group_to_join
        group_request1.save()
        return redirect(reverse('show_groups'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def request_cash(request,pk):
    try:
        
        if request.method == 'POST':
            form = get_amount(request.POST)
            if form.is_valid():
                t_amount = form['amt'].value()
                if float(t_amount) < 0:
                    return redirect(reverse('profilepage'))
                request.session['amount']=t_amount
                money_request = money_requests()
                money_request.amount = t_amount
                money_request.from_user = request.user
                try:
                    other_user = User.objects.get(pk=pk)
                except:
                    return redirect(reverse('homepage'))
                money_request.to_user = other_user
                money_request.save()
                return redirect(reverse('profilepage'))
        else:
            form = get_amount(instance=request.user)
            args = {'form': form}
            return render(request, 'users/request_cash.html', args)
    except:
        return redirect(reverse('homepage'))

@otp_required
def accept_cash_request(request,pk):
    try:
        
        try:
            the_request = money_requests.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        request.session['amount']=float(the_request.amount)
        other_user = the_request.from_user
        if Friend.objects.are_friends(request.user,other_user)==False:
            return redirect(reverse('profilepage'))
        if float(the_request.amount) > request.user.account_balance or float(the_request.amount)<0:
            print("\n\nnot un-friends\n\n")
            return redirect(reverse('profilepage'))
        return redirect(reverse("otp_reverify",kwargs={'plan':'confirm_accept_cash_request','pk':pk}))
    except:
        return redirect(reverse('homepage'))

@otp_required
def confirm_accept_cash_request(request,pk):
    try:
        
        user2 = User.objects.get(pk=request.user.id)
        try:
            the_request = money_requests.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        request.session['amount']=float(the_request.amount)
        other_user2 = the_request.from_user
        if request.session['reverify']==1 and Friend.objects.are_friends(user2,other_user2)==True and request.session['amount']<user2.account_balance:
            with transaction.atomic():
                user1 = User.objects.select_for_update().get(pk=user1.id)
                other_user = User.objects.select_for_update().get(pk=other_user.pk)
                user1.account_balance = user1.account_balance - float(request.session['amount'])
                other_user.account_balance += request.session['amount']
                other_user.save()
                request.session['amount']=0
                request.session['reverify']=None
                user1.save()
                the_request.delete()
            return redirect(reverse('profilepage'))
        else:
            print("\n\nNot Here:(\n\n")
            request.session['reverify']=None
            return redirect(reverse('profilepage'))

        return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def reject_cash_request(request,pk):
    try:

        try:
            the_request = money_requests.objects.get(pk=pk)
        except:
            return redirect(reverse('homepage'))
        the_request.delete()
        return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def confirm_reject_cash_request(request,pk):
    try:
        return redirect(reverse('profilepage'))
    except:
        return redirect(reverse('homepage'))

@otp_required
def my_pages(request):
    try:
        
        if request.user.commercial_user==False:
            return redirect(reverse('profilepage'))
        else:
            lis = Pages.objects.filter(user_id=request.user.id)
            print(lis)
            args = {'lis':lis,}
            return render(request, 'users/my_pages.html', args)
    except:
        return redirect(reverse('homepage'))

@otp_required
def create_page(request):
    try:
        
        if request.user.commercial_user==False:
            return redirect(reverse('profilepage'))
        else:
            if request.method == 'POST':
               form = page_form(request.POST,request.FILES)
               if form.is_valid():
                   post = form.save(commit=False)
                   post.user = request.user
                   post.save()
                   return redirect(reverse('profilepage'))

            else:
                form = page_form()
                args = {'form': form}
                return render(request, 'users/create_page.html', args)
    except:
        return redirect(reverse('homepage'))


@otp_required
def show_page(request,pk1):
    try:
        try:
            page = Pages.objects.filter(pk=pk1)
        except:
            return redirect(reverse('homepage'))
        args = {'title':page[0].title,'body':page[0].content,'url':page[0].img.url}# pass title and body
        return render(request, 'users/show_page.html', args)
    except:
        return redirect(reverse('homepage'))


# @otp_required
# def pages(request):
#     if request.user.commercial_user==False:
#         return redirect(reverse('profilepage'))
#     else:
#         args = {}
#         return render(request, 'users/my_pages.html', args)
    # if request.method == 'POST':
    #     form = PasswordChangeForm(data=request.POST, user=request.user)
    #     if form.is_valid():
    #         form.save()
    #         update_session_auth_hash(request, form.user)
    #         return redirect(reverse('profilepage'))
    #     else:
    #         return redirect(reverse('change_password'))

    # else:
    #     form = PasswordChangeForm(user=request.user)
    #     args = {'form': form }
    #     return render(request, 'users/change_password.html', args)