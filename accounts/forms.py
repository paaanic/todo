from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.forms import EmailField

from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields