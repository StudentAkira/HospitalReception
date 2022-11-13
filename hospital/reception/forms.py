from django import forms
from reception.models import CustomUser, Disease


class RegisterForm(forms.ModelForm):
    password = forms.CharField(required=True, widget=forms.PasswordInput())

    class Meta:
        model = CustomUser
        fields = '__all__'


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=127)
    password = forms.CharField(required=True, widget=forms.PasswordInput())


class DiseaseForm(forms.ModelForm):
    class Meta:
        model = Disease
        exclude = ['discovered_at', 'card']
