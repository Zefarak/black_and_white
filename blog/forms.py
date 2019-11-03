from django import forms

from site_settings.forms import BaseForm
from .models import Post, Photo


class PostForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'


class PostPhotoUploadForm(BaseForm):
    image = forms.ImageField()