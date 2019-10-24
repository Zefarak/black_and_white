from django import forms
from dal import autocomplete

from site_settings.forms import BaseForm
from catalogue.autocomplete_widgets import BrandAutocomplete

from .models import ChartSize


class ChartSizeForm(BaseForm, forms.ModelForm):
    
    class Meta:
        model = ChartSize
        fields = ['active', 'title', 'image', 'brand']
        widgets = {
            'profile': autocomplete.ModelSelect2(url='catalogue:autocomplete_brands', attrs={
                'class': 'form-control', }
                                                 )
        }

