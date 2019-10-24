from django import forms
from .models import Group
class GroupCreationform(forms.ModelForm):

    class Meta:
        model = Group
        fields = ('name','price','privacy')