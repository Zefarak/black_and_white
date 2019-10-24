from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Sum, F
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
from site_settings.models import Country
from site_settings.constants import CURRENCY, POSITIVE_ORDER_TYPES, NEGATIVE_ORDER_TYPES

from decimal import Decimal


class CostumerAccountManager(models.Manager):

    def eshop_costumer(self):
        return super(CostumerAccountManager, self).filter(is_eshop=True)

    def have_balance(self):
        return super().filter(balance__gt=0)


class Profile(models.Model):
    PROFILE_TYPES = (('a', 'Πελατης Λιανικης'), ('b', 'Πελατης Eshop'))
    profile_type = models.CharField(max_length=1, choices=PROFILE_TYPES, default='a')
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE, related_name='profile')
    email_confirmed = models.BooleanField(default=False)
    first_name = models.CharField(blank=True, null=True, max_length=150, verbose_name='Όνομα')
    last_name = models.CharField(blank=True, null=True, max_length=150, verbose_name='Επίθετο')
    notes = models.TextField(blank=True, verbose_name='Σημειώσεις')
    #  shipping_information
    shipping_address = models.CharField(max_length=100, blank=True, null=True, verbose_name='Διεύθυνση Αποστολής')
    shipping_city = models.CharField(max_length=50, blank=True, null=True, verbose_name='Πόλη')
    shipping_zip_code = models.IntegerField(blank=True, null=True, verbose_name='Τκ')
    #  billing information
    billing_name = models.CharField(max_length=100, blank=True, null=True)
    billing_address = models.CharField(max_length=100, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_zip_code = models.IntegerField(blank= True, null=True, )
    #  personal stuff
    phone = models.CharField(max_length=10, blank=True, verbose_name="Τηλέφωνο")
    phone1 = models.CharField(max_length=10, blank=True, verbose_name="Τηλέφωνο 1")
    cellphone = models.CharField(max_length=10, blank=True, verbose_name='Κινητό')
    fax = models.CharField(max_length=10, blank=True, verbose_name="Fax")
    #  if costumer is not Retail
    is_retail = models.BooleanField(default=True)
    is_eshop = models.BooleanField(default=True)
    vat = models.CharField(max_length=9, blank=True, verbose_name="ΑΦΜ")
    vat_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Εφορία')
    value = models.DecimalField(max_digits=20, decimal_places=2, default=0.00,
                                help_text='Off the record Manual Balance', verbose_name='Επιπλέον Αξία')
    balance = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, verbose_name='Υπόλοιπο')
    my_query = CostumerAccountManager()
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.balance = self.calculate_balance()
        self.profile_type = 'b' if self.user else 'a'
        super().save(*args, **kwargs)

    def calculate_balance(self):
        qs = self.profile_orders.all()
        orders = qs.filter(order_type__in=POSITIVE_ORDER_TYPES)
        return_orders = qs.filter(order_type__in=NEGATIVE_ORDER_TYPES)
        orders_sum = orders.aggregate(Sum('final_value'))['final_value__sum'] if orders.exists() else 0.00
        return_orders_sum = return_orders.aggregate(Sum('final_value'))['final_value__sum'] if return_orders.exists() else 0.00
        total_value = Decimal(orders_sum) - Decimal(return_orders_sum)
        paid_value = orders.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if orders.filter(is_paid=True).exists() else 0.00
        return total_value - Decimal(paid_value)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}' if self.first_name else 'No User'

    def get_edit_url(self):
        return reverse('point_of_sale:costumer_update_view', kwargs={'pk': self.id})

    def get_card_url(self):
        return reverse('point_of_sale:costumer_account_card', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('point_of_sale:costumer_delete_view', kwargs={'pk': self.id})

    def template_tag_balance(self):
        return '%s %s' % ('{0:2f}'.format(round(self.balance, 2)),CURRENCY)

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_phones(self):
        return f'{self.cellphone} - {self.phone} - {self.phone1}'

    def tag_full_address(self):
        return f'{self.shipping_address} - {self.shipping_city}'

    def tag_first_name(self):
        return f'{self.first_name}' if self.first_name else None

    def tag_last_name(self):
        return f'{self.last_name}' if self.last_name else None

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

    def update_fields(self, form):
        self.first_name = form.cleaned_data.get('first_name', self.first_name)
        self.last_name = form.cleaned_data.get('last_name', self.last_name)
        self.shipping_address_1 = form.cleaned_data.get('address', self.shipping_address_1)
        self.shipping_city = form.cleaned_data.get('city', self.shipping_city)
        self.shipping_zip_code = form.cleaned_data.get('zip_code', self.shipping_zip_code)
        self.cellphone = form.cleaned_data.get('cellphone', self.cellphone)
        self.phone = form.cleaned_data.get('phone', self.phone)
        self.save()

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)

        queryset = queryset.filter(Q(first_name__contains=search_name) |
                                   Q(last_name__contains=search_name) |
                                   Q(cellphone__contains=search_name) |
                                   Q(phone__contains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


@receiver(post_save, sender=User)
def create_profile(sender, instance, *args, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    profile.first_name = instance.first_name
    profile.last_name = instance.last_name
    profile.save()


class Wishlist(models.Model):
    profile_related = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='wishlist')
    products = models.ManyToManyField('catalogue.Product')

    def __str__(self):
        return self.profile_related


# will be removed
class GuestEmail(models.Model):
    email = models.EmailField()
    timestamp = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.email
