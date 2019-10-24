from django import forms
from django.forms import formset_factory
from .models import Attribute, Cart
from site_settings.models import Shipping, PaymentMethod
from catalogue.models import Product


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CartForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Cart
        fields = '__all__'
        read_only = ['cart_id']


class CartAttributeForm(forms.Form):
    attributes = forms.ModelChoiceField(queryset=Attribute.objects.all())


CartAttributeFormset = formset_factory(CartAttributeForm, extra=2)


class CheckOutForm(BaseForm):
    first_name = forms.CharField(label='Όνομα *')
    last_name = forms.CharField(label='Επώνυμο *')
    email = forms.EmailField(label='Email *')
    address = forms.CharField(label='Διεύθυνση *')
    city = forms.CharField(label='Πόλη *')
    zip_code = forms.CharField(label='TK *', max_length=5)
    cellphone = forms.CharField(label='Κινητό *')
    phone = forms.CharField(label='Σταθερό τηλέφωνο', required=False)
    notes = forms.CharField(label='Σημειώσεις', widget=forms.Textarea(), required=False)
    shipping_method = forms.ModelChoiceField(required=True, queryset=Shipping.objects.filter(active=True),
                                             label='Τρόπος Μεταφοράς *')
    payment_method = forms.ModelChoiceField(required=True, queryset=PaymentMethod.my_query.active_for_site(),
                                            label='Τρόπος Πληρωμής *', )

    agree = forms.BooleanField(label='Συμφωνώ με τους όρους χρήσης *', widget=forms.CheckboxInput())

    def clean_cellphone(self):
        cellphone = self.cleaned_data.get('cellphone')
        if not str(cellphone).startswith('69'):
            raise forms.ValidationError('Ο αριθμος πρεπει να ξεκινάει από 69')
        return cellphone


class ProductCartForm(BaseForm):
    qty = forms.IntegerField(required=True)

