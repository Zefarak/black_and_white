from django import forms
from .models import ProductDiscount
from site_settings.forms import BaseForm


class ProductDiscountForm(BaseForm, forms.ModelForm):
    date_start = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_end = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = ProductDiscount
        fields = ['title', 'date_start', 'date_end', 'active', 'discount_type', 'value']

    def clean_date_end(self):
        date_start = self.cleaned_data.get('date_start', None)
        date_end = self.cleaned_data['date_end']
        if date_end and date_start:
            if date_start > date_end:
                raise forms.ValidationError('Έχετε βάλει λάθος ημερομηνίες')
        return date_end
