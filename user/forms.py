from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', max_length=128)

class SellerCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name',)

class SellerChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'is_active',)