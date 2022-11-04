from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(required=True, max_length=127)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
    fio = forms.CharField(required=True, max_length=127)
    role = forms.ChoiceField(required=True, choices=(
        ('Patient', 'Patient'),
        ('Doctor', 'Doctor'),
    ))


class LoginForm(forms.Form):
    username = forms.CharField(required=True, max_length=127)
    password = forms.CharField(required=True, widget=forms.PasswordInput())
