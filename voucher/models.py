from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.shortcuts import reverse

from catalogue.models import Product, ProductClass, Category, Brand
from .tools import calculate_product_benefit_helper


class Voucher(models.Model):
    SINGLE_USE, MULTI_USE, ONCE_PER_CUSTOMER = (
        'Single use', 'Multi-use', 'Once per customer')
    USAGE_CHOICES = (
        (SINGLE_USE, _("Χρήση μόνο μια φορά")),
        (MULTI_USE, _("Πολλαπλή Χρήση από όλους")),
        (ONCE_PER_CUSTOMER, _("Χρήση μια φορά ανά Πελάτη")),
    )
    active = models.BooleanField(default=False, verbose_name='Κατάσταση')
    name = models.CharField(_("Name"), max_length=128, help_text="This will be shown in the checkout"
                                        " and basket once the voucher is"
                                        " entered")
    code = models.CharField(_('Code'), max_length=128, db_index=True, unique=True)
    usage = models.CharField(max_length=128, choices=USAGE_CHOICES, default=MULTI_USE, verbose_name='Είδος Χρήσης')
    start_date = models.DateField(db_index=True, blank=True, null=True, verbose_name='Χρήση από')
    end_date = models.DateField(db_index=True, blank=True, null=True, verbose_name='Χρήση εώς')
    num_basket_additions = models.PositiveIntegerField(default=0, verbose_name='Συνολικές Προσθήκες στο καλάθι')
    num_orders = models.PositiveIntegerField(default=0, verbose_name='Συνολικές Προσθήκες στις Παραγγελίες')
    total_discount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def get_edit_url(self):
        return reverse('vouchers:voucher_detail', kwargs={'pk': self.id})

    def check_if_its_available(self, instance, user, voucher):
        # first step of checking if voucher can be added to cart or order
        is_available, message = self.is_available_to_user(instance, voucher, user)
        if not is_available:
            return is_available, message
        voucher_rule = self.voucher_rule
        if voucher_rule.exclusive and len(instance.vouchers.all()) > 0:
            is_available, message = False, 'Δε μπορείτε να προσθέσετε αυτό το κουπόνι.'
        if not is_available:
            return is_available, message
        #  starts the calculate
        return is_available, message

    def is_expired(self):
        now = timezone.now()
        return self.end_date < now if self.end_date else False

    def is_available_to_user(self, instance, voucher, user=None):
        is_available, message = False, ''
        if self.is_expired():
            return False, 'Το κουπόνι έχει λήξει.'
        if self.usage == self.SINGLE_USE:
            is_available = instance.check_voucher_if_used(voucher)
            if not is_available:
                message = _("This voucher has already been used")
                return False, message
        if self.usage == self.MULTI_USE:
            is_available, message = True, ''
            return is_available, message
        if self.usage == self.ONCE_PER_CUSTOMER:
            if not user.is_authenticated:
                is_available = False
                message = _('Πρέπει να είσαι χρήστης για να χρησιμοποιήσης αυτό το κουπόνι')
            else:
                profile = user.profile
                user_orders = profile.profile_orders.all()
                orders_with_voucher = user_orders.filter(vouchers=voucher)
                if orders_with_voucher.exists():
                    is_available, message = False, 'Έχετε χρησιμοποιήσει ήδη το κουπόνι'
                else:
                    is_available, message = True, 'Το κουπόνι προστέθηκε με επυτιχία'
            return is_available, message
        return is_available, message

    @staticmethod
    def check_queryset_for_exclusive(queryset):
        #  we use it on cart or order to determind if there is a exclusive voucher
        rules = VoucherRules.objects.filter(voucher__in=queryset)
        if rules.exists():
            return True, rules.first()
        else:
            return False, ''

    @staticmethod
    def calculate_discount_value(instance, vouchers):
        #  instance can be cart or order
        value = 0
        exclusive, rules = Voucher.check_queryset_for_exclusive(vouchers)
        if exclusive:
            return rules.calculate_benefit(instance)
        for voucher in vouchers:
            voucher_rule = voucher.voucher_rule
            val = voucher_rule.calculate_benefit(instance)
            print('added val', val)
            value += val
        print('total val', value)
        return value


class VoucherRules(models.Model):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='voucher_rule')
    SITE, CATEGORY, BRAND, PRODUCTS = ("Site", "Category", "Brand", "Products")
    TYPE_CHOICES = (
        (SITE, _("Site offer - available to all users and products")),
        (CATEGORY, _("Category offer - only available for certain categories ")),
        (BRAND, _("Brand offer - available to certain brands")),
        (PRODUCTS, _("Products offer - Manual add Products")),
    )

    description = models.TextField(blank=True, help_text='Description for the costumers')
    offer_type = models.CharField(choices=TYPE_CHOICES, default=SITE, max_length=128)
    exclusive = models.BooleanField(default=True)
    PERCENTAGE, FIXED, MULTIBUY, FIXED_PRICE = (
        "Percentage", "Absolute", "Multibuy", "Fixed price")
    SHIPPING_ABSOLUTE = 'Shipping absolute'
    TYPE_CHOICES = (
        (PERCENTAGE, _("Discount is a percentage off of the product's value")),
        (FIXED, _("Discount is a fixed amount off of the product's value")),
        (MULTIBUY, _("Discount is to give the cheapest product for free")),
        (FIXED_PRICE,
         _("Reduce the cost of order by the value")),
        (SHIPPING_ABSOLUTE,
         _("Discount is a fixed amount of the shipping cost")),
    )
    benefit_type = models.CharField(_('Discount Type'), choices=TYPE_CHOICES, default=PERCENTAGE, max_length=128)

    value = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)

    priority = models.IntegerField(default=0, db_index=True)

    max_global_applications = models.PositiveIntegerField(blank=True, null=True)
    max_user_applications = models.PositiveIntegerField(blank=True, null=True)
    max_basket_applications = models.PositiveIntegerField(blank=True, null=True)
    total_discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=12)
    num_applications = models.PositiveIntegerField(default=0)
    num_orders = models.PositiveIntegerField(default=0)

    def calculate_benefit(self, instance):
        value = 0
        if self.benefit_type == self.SHIPPING_ABSOLUTE:
            return instance.shipping_method_cost
        if self.benefit_type == self.PERCENTAGE:
            return self.voucher.voucher_range.calculate_benefit_for_percentage(instance, self.offer_type, self.value)
        if self.benefit_type == self.FIXED:
            return self.voucher.voucher_range.calculate_benefit_for_fixed(instance, self.offer_type, self.value)
        return value


class ProductRange(models.Model):
    voucher = models.OneToOneField(Voucher, on_delete=models.CASCADE, related_name='voucher_range')
    include_all_products = models.BooleanField(default=True)
    included_products = models.ManyToManyField(Product, related_name='included_products')
    excluded_products = models.ManyToManyField(Product, related_name='excluded_products')
    classes = models.ManyToManyField(ProductClass)
    included_categories = models.ManyToManyField(Category)
    included_brands = models.ManyToManyField(Brand)

    def calculate_benefit_for_percentage(self, instance, offer_type, value):
        return calculate_product_benefit_helper(self, instance, offer_type, value, self.voucher.voucher_rule.PERCENTAGE)

    def calculate_benefit_for_fixed(self, instance, offer_type, value):
        return calculate_product_benefit_helper(self, instance, offer_type, value, self.voucher.voucher_rule.FIXED)

    def calculated_benefit_for_fixed_price(self, instance, offer_type, value):
        return calculate_product_benefit_helper(self, instance, offer_type, value, self.voucher.voucher_rule.FIXED_PRICE)

    def check_product(self, product, offer_type):
        if offer_type == 'Categories':
            product_categories = product.category_site.all()
            for ele in product_categories:
                if ele in self.included_categories:
                    return True
        if offer_type == 'Brands':
            return product.brand in self.included_brands
        if offer_type == 'products':
            return product in self.included_products
        return False



        








