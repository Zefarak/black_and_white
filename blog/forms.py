from django import forms

from site_settings.forms import BaseForm
from .models import Post, PostCategory


class PostForm(BaseForm, forms.ModelForm):
    date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}),required=False)

    class Meta:
        model = Post
        fields = ['status', 'title', 'category', 'image', 'text', 'date', 'show_custom_date', 'slug']


class PostPhotoUploadForm(BaseForm):
    image = forms.ImageField()


class PostCategoryForm(BaseForm, forms.ModelForm):

    class Meta:
        model = PostCategory
        fields = ['active', 'title', 'image', 'slug']
