from django import forms

from site_settings.forms import BaseForm
from .models import Post, PostCategory, YouTubeVideo


class PostForm(BaseForm, forms.ModelForm):
    date = forms.DateTimeField(widget=forms.DateInput(attrs={'type': 'date'}),required=False)

    class Meta:
        model = Post
        fields = ['status', 'show_first_page', 'title', 'category', 'image', 'text', 'date', 'show_custom_date', 'slug']


class PostPhotoUploadForm(BaseForm):
    image = forms.ImageField()


class PostCategoryForm(BaseForm, forms.ModelForm):

    class Meta:
        model = PostCategory
        fields = ['active', 'title', 'image', 'slug']


class YoutubeVideoForm(BaseForm, forms.ModelForm):
    post_related = forms.ModelChoiceField(queryset=Post.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = YouTubeVideo
        fields = '__all__'