from django import forms
from django.contrib.auth import forms as auth_forms
from users.models import UserWithAvatar


class SignUpForm(auth_forms.UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = UserWithAvatar
        fields = ('username', 'email', 'password1', 'password2',)


class UserProfileForm(forms.Form):
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control',
                                        'type': "text",
                                        'id': 'id_email',
                                        'placeholder': ''}
                             ))
    avatar = forms.ImageField(required=False)


class LoginForm(auth_forms.AuthenticationForm):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control bg-white',
                                          'type': "text",
                                          'id': 'id_username',
                                          'placeholder': ''}
                               ))

    password = forms.CharField(required=True,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control bg-white',
                                          'type': "password",
                                          'id': 'id_password',
                                          'placeholder': ''}
                               ))
