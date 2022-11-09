from django import forms
from reception.models import CustomUser


class RegisterForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=127)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
