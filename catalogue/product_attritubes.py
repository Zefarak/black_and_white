from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django.db.models.signals import post_delete
from django.dispatch import receiver

from mptt.models import MPTTModel, TreeForeignKey
from site_settings.abstract_models import DefaultBasicModel
from site_settings.constants import CURRENCY
from .models import Product
from .managers import AttributeManager, CharacteristicManager
from site_settings.constants import WAREHOUSE_ORDERS_TRANSCATIONS


class Characteristics(DefaultBasicModel):
    title = models.CharField(max_length=120, unique=True, verbose_name='Τίτλος')
    is_filter = models.BooleanField(default=False, verbose_name='Εμφάνιση στα Φίλτρα')

    browser = CharacteristicManager()
    objects = models.Manager()

    class Meta:
        app_label = 'catalogue'

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:char_edit_view', kwargs={'pk': self.id})


class CharacteristicsValue(DefaultBasicModel):
    title = models.CharField(max_length=120, unique=True)
    char_related = models.ForeignKey(Characteristics, on_delete=models.SET_NULL, null=True, related_name='my_values')
    custom_ordering = models.IntegerField(default=0, verbose_name='Ordering', help_text='Bigger is better')

    class Meta:
        app_label = 'catalogue'
        ordering = ['-custom_ordering', 'title']

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:char_value_edit_view', kwargs={'pk': self.id})


class ProductCharacteristics(models.Model):
    product_related = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics')
    title = models.ForeignKey(Characteristics, on_delete=models.CASCADE)
    value = models.ForeignKey(CharacteristicsValue, on_delete=models.CASCADE, related_name='my_value')
    objects = models.Manager()

    class Meta:
        app_label = 'catalogue'
        unique_together = ('product_related', 'title')

    def __str__(self):
        return f'{self.title.title} - {self.value.title}'

    @staticmethod
    def filters_data(request, qs):
        char_name = request.GET.getlist('char_name', None)
        try:
            chars_selected = CharacteristicsValue.objects.filter(id__in=char_name).distinct()
            prod_char = ProductCharacteristics.objects.filter(value__in=chars_selected)
            products_ids = prod_char.values_list('product_related__id')
            qs = qs.filter(id__in=products_ids)
        except:
            qs = qs
        return qs


class AttributeClass(models.Model):
    title = models.CharField(unique=True, max_length=150)
    have_transcations = models.BooleanField(default=True, verbose_name='Υποστηρίζει Συναλλαγές')

    class Meta:
        verbose_name_plural = 'Attribute Class Title'

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:attribute_class_edit_view', kwargs={'pk': self.id})


class AttributeTitle(MPTTModel):
    timestamp = models.DateField(auto_now=True)
    attri_by = models.ForeignKey(AttributeClass, null=True, on_delete=models.CASCADE, related_name='my_values')
    name = models.CharField(max_length=120, verbose_name='Τίτλος')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        unique_together = ['name', 'attri_by']
        app_label = 'catalogue'
        verbose_name_plural = 'Τιμες Μεγεθολόγιου'

    def __str__(self):
        return self.name

    def get_edit_url(self):
        return reverse('dashboard:attribute_title_edit_view', kwargs={'pk': self.id})


class AttributeProductClass(models.Model):
    class_related = models.ForeignKey(AttributeClass, on_delete=models.CASCADE)
    product_related = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, verbose_name='Προϊόν',
                                        related_name='attr_class')

    class Meta:
        verbose_name_plural = 'Product Attribute Class'

    def __str__(self):
        return f'{self.class_related.title} {self.product_related}'


class Attribute(models.Model):
    title = models.ForeignKey(AttributeTitle, on_delete=models.CASCADE, related_name='sizes')
    class_related = models.ForeignKey(AttributeProductClass, on_delete=models.CASCADE, related_name='my_attributes')
    qty = models.IntegerField(default=0, verbose_name='Ποσότητα')
    qty_add = models.IntegerField(default=0.00, verbose_name="Υπόλοιπο", help_text='we use this for manual add.')
    qty_remove = models.IntegerField(default=0.00, verbose_name="Qty Remove", help_text='System use it only if warehouse transations')
    order_discount = models.IntegerField(null=True, blank=True, default=0, verbose_name="'Εκπτωση Τιμολογίου σε %")
    price_buy = models.DecimalField(decimal_places=2, max_digits=6, default=0, verbose_name="Τιμή Αγοράς")

    show_on_site = models.BooleanField(default=True)
    my_query = AttributeManager()
    objects = models.Manager()

    class Meta:
        app_label = 'catalogue'
        verbose_name_plural = 'Attribute'

        ordering = ['title']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            self.qty_add = self.calculate_warehouse()
            self.qty = self.qty_add
        self.show_on_site = False if self.qty <= 0 else True
        self.class_related.product_related.save()

    def __str__(self):
        return f'{self.title}'

    def calculate_warehouse(self):
        invoices_items = self.invoice_attributes.all()
        items_added = invoices_items.filter(order_item__order__order_type__in=[['1', '2', '4']])
        item_removed = invoices_items.filter(order_item__order__order_type='5')
        items_added = items_added.aggregate(Sum('qty'))['qty__sum'] if items_added.exists() else 0
        items_removed = item_removed.aggregate(Sum('qty'))['qty__sum'] if item_removed.exists() else 0
        return items_added - items_removed

    def check_product_in_order(self):
        return str(self.product_related + '. Χρώμα : ' + self.title.title + ', Μέγεθος : ' + self.title.title)

    @staticmethod
    def filters_data(request, queryset):
        size_name = request.GET.getlist('size_name', None)
        print('here attr')
        queryset = queryset.filter(title__id__in=size_name) if size_name else queryset
        return queryset

    @staticmethod
    def product_filter_data(request, products_qs):
        attr_name = request.GET.getlist('attr_name', None)
        qs = Attribute.objects.filter(class_related__product_related__in=products_qs, title__id__in=attr_name).distinct()
        products_ids = qs.values_list('class_related__product_related__id')
        return Product.objects.filter(id__in=products_ids)


@receiver(post_delete, sender=Attribute)
def update_qty_on_product(sender, instance, **kwargs):
    class_related = instance.class_related
    product = class_related.product_related
    product.save()

