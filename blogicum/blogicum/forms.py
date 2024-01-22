from django import forms
from django.forms import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .constants import DENIED_USERNAMES


User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username in DENIED_USERNAMES:
            raise ValidationError('Использование этого имени запрещено.')
        return username


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
