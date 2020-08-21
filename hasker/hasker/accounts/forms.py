from django import forms
from django.contrib.auth.forms import (
	UserCreationForm,
	UserChangeForm,
	AuthenticationForm
)
from .models import Account


class AccountCreationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = Account
        fields = UserCreationForm.Meta.fields + ('email', 'avatar')
        labels = {'avatar': 'Choose avatar:'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


class AccountChangeForm(UserChangeForm):

    class Meta:
        model = Account
        fields = ('email', 'avatar')
        widgets = {
            "avatar": forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['avatar'].required = False


class EmailChangeForm(UserChangeForm):

    class Meta:
        model = Account
        fields = ('email',)


class AvatarChangeForm(UserChangeForm):

    class Meta:
        model = Account
        fields = ('avatar',)
        widgets = {
            "avatar": forms.FileInput(),
        }



class AccountAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'
