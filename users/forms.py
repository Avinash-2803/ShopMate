from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class':'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500'   
            })


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget= forms.TextInput())
    password = forms.CharField(widget= forms.PasswordInput())


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email']
        exclude = ['password1', 'password2']
        