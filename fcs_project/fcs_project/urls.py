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
from django.urls import path
from django.contrib.auth import views as auth_views
from django_otp.forms import OTPAuthenticationForm
from users.forms import SimpleOTPAuthenticationForm
from users import views as user_views
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.admin import OTPAdminSite
class OTPAdmin(OTPAdminSite):
    pass

admin_site=OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice)
urlpatterns = [
    path('otp_setup/',user_views.otpsetup,name='otpsetup'),
    path('cancel_plan/',user_views.cancel_plan,name='cancel_plan'),
    path('view_friend/(?P<pk>\d+)',user_views.view_friend,name='view_friend'),
    path('add_friend/(?P<pk>\d+)',user_views.add_friend,name='add_friend'),
    path('change_password/',user_views.changepass,name='change_password'),
    path('upgrade/',user_views.upgrade,name='upgrade'),
    path('silver_plan/',user_views.silver_plan,name='Silver_plan'),
    path('gold_plan/',user_views.gold_plan,name='Gold_plan'),
    path('get_silver/',user_views.get_silver,name='get_silver'),
    path('get_gold/',user_views.get_gold,name='get_gold'),
    path('get_platinum/',user_views.get_platinum,name='get_platinum'),
    path('platinum_plan/',user_views.platinum_plan,name='Platinum_plan'),
    path('editprofile/',user_views.editprofile,name='editprofile'),
    path('profilepage/',user_views.profilepage,name='profilepage'),
    path('options/',user_views.options,name='useroptions'),
    path('welcome/',user_views.welcome,name='welcomepage'),
    path('home',user_views.home,name='homepage'),
    path('',user_views.welcome, name='home'),
    path('/',user_views.welcome, name='home'),
    path('timeline/(?P<pk>\d+)',user_views.timeline,name='Timeline'),
    path('login/', auth_views.LoginView.as_view(authentication_form=SimpleOTPAuthenticationForm,template_name='users/login.html'), name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('signup/', user_views.signup, name='signup'),
    path('admin/', admin.site.urls),
    path('adminotp/', admin_site.urls),
    path('accept_request/(?P<pk>\d+)',user_views.accept_request,name='accept_request'),
    path('reject_request/(?P<pk>\d+)',user_views.reject_request,name='reject_request'),
    path('remove_friend/(?P<pk>\d+)',user_views.remove_friend,name='remove_friend')
]
