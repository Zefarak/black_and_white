from django import forms

from site_settings.forms import BaseForm



class OrderStatusForm(BaseForm):
    order_code = forms.CharField(label='Κωδικός Παραγγελίας')


class AskForm(BaseForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    message = forms.CharField(widget=forms.Textarea(), required=False)
    
    
