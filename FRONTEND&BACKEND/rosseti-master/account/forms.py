from django import forms
# from account.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import Profile


User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=150, help_text=_('Required. Add a valid email address'))

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "gender", "password1", "password2"]


class UserRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Password do not match'))

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(max_length=150, help_text=_('Required. Add a valid email address'))

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "gender"]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'birthday', 'job_title', 'phone', 'firma_name', 'linkedin', 'facebook', 'vkontakte', 'instagram', 'email_notify']