from django import forms

from site_settings.forms import BaseForm
from .models import Subscribe, UserSubscribe


class SubscribeForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Subscribe
        fields = ['active', 'title', 'category', 'counter', 'value', 'ordering']


class UserSubscribeForm(BaseForm, forms.ModelForm):

    class Meta:
        model = UserSubscribe
        fields = ['user', 'subscription', 'active']
