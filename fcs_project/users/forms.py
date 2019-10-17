from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User,UserProfile


class SignUpForm(UserCreationForm):

    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields+('first_name','last_name','email')

class EditProfileForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password',
        )

class EditProfileFormextend(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = (
            'description',
            'city',
            'phone',
            'privacy',
        )