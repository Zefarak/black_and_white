from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from .constants import CURRENCY
from .managers import PaymentMethodManager, ShippingManager
from tinymce.models import HTMLField

from decimal import Decimal


def validate_size(value):
    if value.file.size > 1024*1024*0.5:
        raise ValidationError('The file is bigger than 0.5mb')


def upload_banner(instance, filename):
    return f'banners/{filename}'


def validate_positive_decimal(value):
    if value < 0:
        return ValidationError('This number is negative!')
    return value


class Company(models.Model):
    company_name = models.CharField(max_length=120, null=True)
    company_address = models.CharField(max_length=200, null=True)
    company_city_zip = models.CharField(max_length=5, null=True)
    company_email = models.EmailField(null=True)
    company_phone = models.CharField(max_length=10, null=True)
    company_fax = models.CharField(max_length=10, null=True)
    logo = models.ImageField(upload_to='company/', null=True)

    def __str__(self):
        return self.company_name


class Country(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=100)

    def __str__(self):
        return self.title


class Shipping(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    title = models.CharField(unique=True,
                             max_length=100,
                             verbose_name='Τίτλος'
                             )
    additional_cost = models.DecimalField(max_digits=6,
                                          default=0,
                                          decimal_places=2,
                                          validators=[validate_positive_decimal, ],
                                          verbose_name='Επιπλέον κόστος'
                                          )
    limit_value = models.DecimalField(default=40,
                                      max_digits=6,
                                      decimal_places=2,
                                      validators=[validate_positive_decimal, ],
                                      verbose_name='Μέγιστη Αξία Κόστους'
                                      )
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    first_choice = models.BooleanField(default=False, verbose_name='Πρώτη Επιλογή')
    ordering_by = models.IntegerField(default=1, verbose_name='Priority Order')
    text = HTMLField(blank=True)
    objects = models.Manager()
    browser = ShippingManager()

    class Meta:
        ordering = ['-ordering_by', ]
        verbose_name_plural = 'Τρόποι Μεταφοράς'

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('site_settings:shipping_edit', kwargs={'pk': self.id})

    def estimate_additional_cost(self, value, voucher=None):
        if value <= 0 or value >= self.limit_value:
            return 0
        return Decimal(self.additional_cost)

    def tag_active_cost(self):
        return f'{self.additional_cost} {CURRENCY}'

    def tag_limit_value(self):
        return f'{self.limit_value} {CURRENCY}'

    def tag_additional_cost(self):
        return f'{self.additional_cost} {CURRENCY}'

    tag_additional_cost.short_description = 'Επιπλέον Κόστος'

    def tag_active(self):
        return 'Active' if self.active else 'No Active'


class PaymentMethod(models.Model):
    PAYMENT_TYPE = (
        ('a', 'Cash'),
        ('b', 'Bank'),
        ('c', 'Credit Card'),
        ('d', 'Internet Service')
    )
    active = models.BooleanField(default=True, verbose_name='Status')
    title = models.CharField(unique=True, max_length=100, verbose_name='Ονομασία')
    payment_type = models.CharField(choices=PAYMENT_TYPE, default='a', max_length=1, verbose_name='Είδος')
    site_active = models.BooleanField(default=False, verbose_name='Εμφάνιση στο Site')
    additional_cost = models.DecimalField(decimal_places=2,
                                          max_digits=10,
                                          default=0,
                                          verbose_name='Μεταφορικά')
    limit_value = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Ελάχιστο Ποσό Χρέωσης')
    first_choice = models.BooleanField(default=False)
    objects = models.Manager()
    my_query = PaymentMethodManager()

    class Meta:
        verbose_name_plural = 'Τρόποι Πληρωμής'

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('site_settings:payment_edit', kwargs={'pk': self.id})

    def tag_additional_cost(self):
        return '%s %s' % (self.additional_cost, CURRENCY)

    tag_additional_cost.short_description = 'Επιπλέον Κόστος'

    def tag_limit_value(self):
        return '%s %s' % (self.limit_value, CURRENCY)

    tag_limit_value.short_description = 'Όριο'

    def estimate_additional_cost(self, value, voucher=None):
        if value <= 0 or value >= self.limit_value:
            return 0.00
        return Decimal(self.additional_cost)

    def get_delete_url(self):
        return reverse('site_settings:payment_delete', kwargs={'pk': self.id})


class Store(models.Model):
    title = models.CharField(unique=True, max_length=100)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Κατάστημα'

    def __str__(self):
        return self.title

    def get_billing_url(self):
        return reverse('warehouse:billing_store_view', kwargs={'pk': self.id})

    def get_edit_url(self):
        return reverse('site_settings:store_edit', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('site_settings:store_delete', kwargs={'pk': self.id})


class BannerManager(models.Manager):

    def active(self):
        return self.filter(active=True)


class Banner(models.Model):
    BANNER_TYPE = (('a', 'Μεγάλο Banner --> (1970*718)'),
                   ('b', 'Μεσαίο Banner --> No Use. For future'),
                   ('c', 'Μικρό Banner -->(600*250)')
                   )
    active = models.BooleanField(default=False, verbose_name='Κατάσταση')
    category = models.CharField(max_length=1, choices=BANNER_TYPE, default='a')
    title = models.CharField(unique=True, max_length=100, verbose_name='Τίτλος')
    text = HTMLField(verbose_name='Σχόλiα', blank=True)
    image = models.ImageField(upload_to=upload_banner, validators=[validate_size, ])
    url = models.URLField(blank=True, null=True)
    bootstrap_class = models.CharField(default='home-slide', max_length=200, help_text='home-slide text-center')
    browser = BannerManager()
    objects = models.Manager()

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('site_settings:banner_edit', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('site_settings:banner_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        active_name = request.GET.get('active_name', None)
        search_name = request.GET.get('search_name', None)
        qs = qs.filter(active=True) if active_name == '1' else qs.filter(active=False) if active_name =='2' else qs
        qs = qs.filter(title__contains=search_name) if search_name else qs
        return qs

class SeoDataModel(models.Model):
    CHOICES = (
        ('a', 'Homepage'),
        ('b', 'Brands'),
        ('c', 'New Products'),
        ('d', 'Offers')
    )
    keywords = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    choice = models.CharField(max_length=1, choices=CHOICES, unique=True)

    def __str__(self):
        return self.get_choice_display()



