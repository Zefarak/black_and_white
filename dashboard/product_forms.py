from django import forms
from django.conf import settings
from catalogue.forms import BaseForm
from catalogue.models import Product

from dal import autocomplete

WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS
RETAIL_TRANSCATIONS = settings.RETAIL_TRANSCATIONS


class ProductFormWarehouseTranscations(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['active',
                  'warehouse_active',
                  'featured_product',
                  'title', 'sku',
                  'vendor', 'order_code',
                  'price_buy', 'order_discount',
                  'brand', 'category',
                  'price', 'price_discount',
                  'qty_measure',
                  'measure_unit',
                  'site_text', 'slug'

                  ]
        widgets = {
            'catalogue:vendor': autocomplete.ModelSelect2(url='catalogue:vendors_auto',
                                                          attrs={'class': 'form-control'}),
            'catalogue:category': autocomplete.ModelSelect2(url='cate:warehouse_category_auto',
                                                            attrs={'class': 'form-control', 'data-html': True}),
            'catalogue:brands': autocomplete.ModelSelect2(url='catalogue:brands_auto',
                                                          attrs={'class': 'form-control'}
                                                          )
        }


class ProductNoQty(BaseForm, forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'sku',
                  'vendor', 'order_code',
                  'price_buy', 'order_discount',
                  'brand', 'category',
                  'price', 'price_discount',
                  'qty_measure', 'measure_unit',
                  'site_text', 'slug',
                  'active', 'featured_product'
                ]
        widgets = {
            'brand': autocomplete.ModelSelect2(url='catalogue:brand-autocomplete',
                                               attrs={'class': 'form-control'}
                                            )
        }


class ProductForm(BaseForm, forms.ModelForm):

    class Meta:
        model = Product
        fields = ['active',
                  'featured_product',
                  'title', 'sku',
                  'color', 'brand',
                  'measure_unit',
                  'price', 'price_discount',
                  'site_text', 'slug',
                  'category',
                  'vendor', 'price_buy',
                ]






