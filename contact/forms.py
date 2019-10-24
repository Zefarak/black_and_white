from django import forms

from .models import Contact
from site_settings.forms import BaseForm


class ContactForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'


class ContactFrontEndForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone_number', 'message']
