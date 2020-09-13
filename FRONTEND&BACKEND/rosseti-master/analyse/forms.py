from django import forms
from .models import Photo


class PhotoForm(forms.ModelForm):
    photo = forms.ImageField(label='Photo')

    class Meta:
        model = Photo
        fields = ('pole', 'image')
