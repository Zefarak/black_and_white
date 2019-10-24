from django import forms
from .models import Voucher, ProductRange, VoucherRules


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class VoucherForm(BaseForm, forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Χρήση Από')
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label='Χρήση Εώς')

    class Meta:
        model = Voucher
        fields = ['active', 'usage', 'name', 'code', 'start_date', 'end_date']


class ProductRangeForm(BaseForm, forms.ModelForm):
    voucher = forms.ModelChoiceField(queryset=Voucher.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = ProductRange
        fields = '__all__'


class VoucherRulesForm(BaseForm, forms.ModelForm):
    voucher = forms.ModelChoiceField(queryset=Voucher.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = VoucherRules
        fields = '__all__'