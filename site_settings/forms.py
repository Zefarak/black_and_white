from django import forms
from .models import Store, PaymentMethod, Shipping, Banner, Company, SeoDataModel


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StoreForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Store
        fields = '__all__'


class PaymentMethodForm(BaseForm, forms.ModelForm):

    class Meta:
        model = PaymentMethod
        fields = ['title', 'payment_type', 'active', 'site_active', 'additional_cost', 'limit_value', 'first_choice']


class ShippingForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Shipping
        fields = ['title', 'active', 'additional_cost', 'limit_value', 'text', 'ordering_by']


class BannerForm(BaseForm, forms.ModelForm):

     class Meta:
         model = Banner
         fields = '__all__'


class CompanyForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Company
        fields = '__all__'


class SeoDataForm(BaseForm, forms.ModelForm):

    class Meta:
        model = SeoDataModel
        fields = '__all__'