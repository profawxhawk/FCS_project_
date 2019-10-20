from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User,UserProfile,posts
from django_otp.forms import OTPAuthenticationForm,OTPTokenForm
from django import forms

class SimpleOTPRegistrationForm(OTPTokenForm):
    otp_device = forms.CharField(required=False, widget=forms.HiddenInput)
    otp_challenge = forms.CharField(required=False, widget=forms.HiddenInput)


class SimpleOTPAuthenticationForm(OTPAuthenticationForm):
    otp_device = forms.CharField(required=False, widget=forms.HiddenInput)
    otp_challenge = forms.CharField(required=False, widget=forms.HiddenInput)

class postform(forms.ModelForm):
    post = forms.CharField(widget=forms.TextInput(
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