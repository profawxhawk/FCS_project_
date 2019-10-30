from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User,UserProfile,posts,transactions,amount,Pages
from django_otp.forms import OTPAuthenticationForm,OTPTokenForm
class SimpleOTPRegistrationForm(OTPTokenForm):
    otp_device = forms.CharField(required=False, widget=forms.HiddenInput)
    otp_challenge = forms.CharField(required=False, widget=forms.HiddenInput)
    otp_token = forms.CharField(required=False,max_length=6,widget=forms.TextInput(attrs={'readonly':'readonly'}))

class otpform(forms.Form):
    otp_token=forms.CharField(required=False,max_length=6,widget=forms.TextInput(attrs={'readonly':'readonly'}))

class SimpleOTPAuthenticationForm(OTPAuthenticationForm):
    otp_device = forms.CharField(required=False, widget=forms.HiddenInput)
    otp_challenge = forms.CharField(required=False, widget=forms.HiddenInput)
 

class postform(forms.ModelForm):
    post = forms.CharField(max_length=300,widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Write a post...'
        }
    ))

    class Meta:
        model = posts
        fields = ('post',)

class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields+('first_name','last_name','email')

class EditProfileForm(UserChangeForm):
    password = None
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
        )

class EditProfileFormextend(UserChangeForm):
    password = None
    class Meta:
        model = UserProfile
        fields = (
            'description',
            'city',
            'phone',
            'privacy',
        )

class get_transaction_amount(forms.ModelForm):
    class Meta:
        model = transactions
        fields = ('amount',)

class page_form(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ('title','content','img')

class get_amount(forms.ModelForm):
    class Meta:
        model = amount
        fields = ('amt',)