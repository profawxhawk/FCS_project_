"""fcs_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django_otp.forms import OTPAuthenticationForm
from users.forms import SimpleOTPAuthenticationForm
from users import views as user_views
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.admin import OTPAdminSite
from chat import views as chat_views
from django.conf import settings
from django.conf.urls.static import static 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import (
handler400, handler403, handler404, handler500
)
class OTPAdmin(OTPAdminSite):
    pass
handler404 = 'users.views.handler404'
handler500 = 'users.views.handler500'
admin_site=OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice)
urlpatterns = [
    path('otp_setup/',user_views.otpsetup,name='otpsetup'),
    path('cancel_plan/',user_views.cancel_plan,name='cancel_plan'),
    path('view_friend/<int:pk>/',user_views.view_friend,name='view_friend'),
    path('add_friend/<int:pk>/',user_views.add_friend,name='add_friend'),
    path('change_password/',user_views.changepass,name='change_password'),
    path('upgrade/',user_views.upgrade,name='upgrade'),
    path('silver_plan/',user_views.silver_plan,name='Silver_plan'),
    path('commercial_plan/',user_views.commercial_plan,name='Commercial_plan'),
    path('gold_plan/',user_views.gold_plan,name='Gold_plan'),
    path('get_silver/',user_views.get_silver,name='get_silver'),
    path('get_commercial/',user_views.get_commercial,name='get_commercial'),
    path('get_gold/',user_views.get_gold,name='get_gold'),
    path('get_platinum/',user_views.get_platinum,name='get_platinum'),
    path('do_transactions/<int:pk>/',user_views.do_transactions,name='do_transactions'),
    path('transactions/',user_views.transaction_occur,name='transactions'),
    path('platinum_plan/',user_views.platinum_plan,name='Platinum_plan'),
    path('editprofile/',user_views.editprofile,name='editprofile'),
    path('profilepage/',user_views.profilepage,name='profilepage'),
    path('options/',user_views.options,name='useroptions'),
    path('welcome/',user_views.welcome,name='welcomepage'),
    path('home',user_views.home,name='homepage'),
    path('',user_views.welcome, name='home'),
    path('/',user_views.welcome, name='home'),
    path('timeline/<int:pk>/',user_views.timeline,name='Timeline'),
    path('login/', auth_views.LoginView.as_view(authentication_form=SimpleOTPAuthenticationForm,template_name='users/login.html'), name='login'),
    path('request_cash/(?P<pk>\d+)',user_views.request_cash,name='request_cash'),
    path('accept_money/<int:pk>/',user_views.accept_money,name='accept_money'),
    path('reject_money/<int:pk>/',user_views.reject_money,name='reject_money'),
    path('logout/', user_views.logout_view, name='logout'),
    path('signup/', user_views.signup, name='signup'),
    path('reverify(?P<plan>[^/]+)/<int:pk>/', user_views.reverify, name='otp_reverify'),
    path('confirm_transactions/<int:pk>/', user_views.confirm_transactions, name='confirm_transactions'),
    path('admin/', admin.site.urls),
    path('adminotp/', admin_site.urls),
    path('show_groups',user_views.show_groups,name="show_groups"),
    path('accept_request/<int:pk>/',user_views.accept_request,name='accept_request'),
    path('reject_request/<int:pk>/',user_views.reject_request,name='reject_request'),
    path('remove_friend/<int:pk>/',user_views.remove_friend,name='remove_friend'),
    path('room/<int:pk>/',chat_views.room,name='room'),
    path('groups/',include('groups.urls')),
    path('send_group_request/<int:pk>',user_views.send_group_request,name='send_group_request'),
    path('add_money/',user_views.add_money,name='add_money'),
    path('confirm_add_money/',user_views.confirm_add_money,name='confirm_add_money'),
    # path('pages/',user_views.pages,name='pages'),
    path('my_pages/',user_views.my_pages,name='my_pages'),
    path('create_page/',user_views.create_page,name='create_page'),
    path('show_page/(?P<pk1>\d+)',user_views.show_page,name='show_page'),
    path('accept_cash_request/(?P<pk>\d+)',user_views.accept_cash_request,name='accept_cash_request'),
    path('reject_cash_request/(?P<pk>\d+)',user_views.reject_cash_request,name='reject_cash_request'),
    path('confirm_accept_cash_request/(?P<pk>\d+)',user_views.confirm_accept_cash_request,name='confirm_accept_cash_request'),
    path('confirm_reject_cash_request/(?P<pk>\d+)',user_views.confirm_reject_cash_request,name='confirm_reject_cash_request'),
    path('confirm_send_group_request/(?P<pk>\d+)',user_views.confirm_send_group_request,name='confirm_send_group_request'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)