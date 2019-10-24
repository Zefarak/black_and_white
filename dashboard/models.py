from django.db import models
from django.shortcuts import reverse
from catalogue.models import Product
from django.db.models import F
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
TYPE = (
    ('a', 'Ποσοστό'),
    ('b', 'Ποσό'),
    ('c', 'Ακριβές Ποσό')
)


class ProductDiscount(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    date_start = models.DateField(verbose_name='Ημερομηνία Από..',
                                  blank=True,
                                  null=True)
    date_end = models.DateField(verbose_name='Ημερομηνία Μέχρι..',
                                help_text='Αν μείνει κενό διαρκεί για πάντα',
                                blank=True,
                                null=True
                                )
    title = models.CharField(unique=True, max_length=200, verbose_name='Τίτλος')
    discount_type = models.CharField(max_length=1, choices=TYPE, verbose_name='Έιδος Έκπτωσης')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Αξία')
    products_related = models.ManyToManyField(Product)

    def __str__(self):
        return self.title

    def tag_range(self):
        return f'{self.date_start} - {self.date_end}'

    def get_edit_url(self):
        return reverse('dashboard:discount_manager_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return ''


@receiver(post_save, sender=ProductDiscount)
def update_prices_to_products(sender, instance, **kwargs):
    qs = instance.products_related.all()
    discount_type = instance.discount_type
    if discount_type == 'a':
        discount_percent = (100-instance.value)/100
        qs.update(price_discount=F('price')*discount_percent, final_price=F('price')*discount_percent)
    if discount_type == 'b':
        remove_price = instance.value
        qs.update(price_discount=F('price')-remove_price, final_price=F('price')-remove_price)
    if discount_type == 'c':
        new_value = instance.value
        qs.update(price_discount=new_value, final_value=new_value)


@receiver(post_delete, sender=ProductDiscount)
def delete_prices_from_products(sender, instance, **kwargs):
    qs = instance.products_related.all()
    qs.update(discount_value=0, final_value=F('price'))
