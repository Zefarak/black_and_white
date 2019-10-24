from django import forms


from .models import NewsLetter


class BaseForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class NewsLetterForm(BaseForm, forms.ModelForm):

    class Meta:
        model = NewsLetter
        fields = '__all__'