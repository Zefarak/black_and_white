from django.db import models
from django.urls import reverse
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.db.models import Sum, Q
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.html import format_html


from decimal import Decimal


from site_settings.constants import TAXES_CHOICES
from catalogue.models import Product
from catalogue.product_attritubes import Attribute, AttributeClass
from .abstract_models import DefaultOrderModel, DefaultOrderItemModel
from site_settings.models import PaymentMethod, Shipping, Country
from site_settings.constants import CURRENCY, ORDER_STATUS, ORDER_TYPES, ADDRESS_TYPES
from site_settings.tools import clean_date_filter
from cart.models import Cart, CartItem, CartItemGifts, CartSubscribe
from .managers import OrderManager, OrderItemManager
from accounts.models import Profile
from voucher.models import Voucher
from subscribe.models import Subscribe, UserSubscribe

RETAIL_TRANSCATIONS, PRODUCT_ATTRIBUTE_TRANSCATIONS, WAREHOUSE_TRANSCATIONS = [settings.RETAIL_TRANSCATIONS,
                                                                               settings.PRODUCT_ATTRIBUTE_TRANSCATIONS,
                                                                               settings.WAREHOUSE_ORDERS_TRANSCATIONS
                                                                               ]
MANUAL_RETAIL_TRANSCATIONS = settings.MANUAL_RETAIL_TRANSCATIONS

POSITIVE_ORDER_TYPES, NEGATIVE_ORDERS_TYPES = ['r', 'e', 'wr'], ['b', 'c', 'wa']
SITE_EMAIL = settings.SITE_EMAIL
User = get_user_model()


class Order(DefaultOrderModel):
    number = models.SlugField(max_length=128, db_index=True, blank=True)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default='1', verbose_name="Κατάσταση")
    order_type = models.CharField(max_length=1, choices=ORDER_TYPES, default='r', verbose_name='Είδος')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                     verbose_name='Συνολικο Κόστος')
    user = models.ForeignKey(User,
                             blank=True,
                             null=True,
                             verbose_name='User Account',
                             on_delete=models.SET_NULL,
                             related_name='orders'
                             )
    profile = models.ForeignKey(Profile,
                                blank=True,
                                null=True,
                                verbose_name='Πελάτης',
                                on_delete=models.SET_NULL,
                                related_name='profile_orders'
                                )

    #  eshop info only
    shipping_method = models.ForeignKey(Shipping, null=True, blank=True, on_delete=models.SET_NULL,
                                        verbose_name='Τρόπος Μεταφοράς')
    shipping_method_cost = models.DecimalField(default=0, decimal_places=2, max_digits=5, verbose_name='Μεταφορικά')
    payment_cost = models.DecimalField(default=0, decimal_places=2, max_digits=5, verbose_name='Κόστος Αντικαταβολής')
    day_sent = models.DateTimeField(blank=True, null=True, verbose_name='Ημερομηνία Αποστολής')
    eshop_session_id = models.CharField(max_length=50, blank=True, null=True)
    my_query = OrderManager()
    objects = models.Manager()
    cart_related = models.OneToOneField(Cart, blank=True, null=True, on_delete=models.SET_NULL, related_name='order')
    # coupons = models.ManyToManyField(Coupons, blank=True)
    order_related = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    voucher_discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    guest_email = models.EmailField(blank=True)
    vouchers = models.ManyToManyField(Voucher, blank=True)
    subscribe_cost = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    subscribe_discount_cost = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    class Meta:
        verbose_name_plural = '1. Orders'
        verbose_name = 'Order'
        ordering = ['-date_expired', 'status', '-id']

    def __str__(self):
        return self.title if self.title else 'order'

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = get_random_string(length=30)
        order_items = self.order_items.all()
        self.count_items = order_items.count() if order_items else 0
        self.voucher_discount = self.handle_vouchers()
        self.update_order()
        self.final_value = self.shipping_method_cost + self.payment_cost + self.value + self.subscribe_cost \
                           - self.discount - self.voucher_discount - self.subscribe_discount_cost
        self.paid_value = self.final_value if self.is_paid else 0
        if self.id:
            self.title = f'{self.get_order_type_display()}- 000{self.id}' if not self.title else self.title
        super().save(*args, **kwargs)
        if self.profile:
            self.profile.save()

    def update_warehouse(self):
        items = self.order_items.all()
        for item in items:
            item.update_warehouse()

    def handle_vouchers(self):
        vouchers = self.vouchers.all() if self.id else Voucher.objects.none()
        discount = 0
        cart = self
        if vouchers.exists():
            discount = Voucher.calculate_discount_value(instance=cart, vouchers=vouchers)
        return round(discount, 2)

    def get_absolute_url(self):
        return reverse('frontend_order_detail', kwargs={'slug': self.number})

    def get_edit_url(self):
        return reverse('point_of_sale:order_detail', kwargs={'pk': self.id})

    def get_eshop_url(self):
        return reverse('point_of_sale:eshop_detail_view', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('point_of_sale:delete_order', kwargs={'pk': self.id})

    def get_detail_url(self):
        return reverse('order_detail', kwargs={'pk': self.id})

    def get_print_url(self):
        return reverse('point_of_sale:print_order', kwargs={'pk': self.id})

    def update_order(self):
        items = self.order_items.all()
        self.value = items.aggregate(Sum('total_value'))['total_value__sum'] if items else 0
        self.total_cost = items.aggregate(Sum('total_cost_value'))['total_cost_value__sum'] if items else 0

    def tag_profile_full_name(self):
        profile = self.order_profiles.first() if self.order_profiles.exists() else None
        if not profile:
            return self.user
        return f'{profile.first_name} {profile.last_name}'

    def tag_address(self):
        profile = self.order_profiles.first() if self.order_profiles.exists() else None
        if profile:
            return f'{profile.address} {profile.city} {profile.zip_code}'
        return 'Δε υπάρχουν δεδομένα'

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)
    tag_final_value.short_description = 'Value'

    def taxes(self):
        return round(Decimal(self.final_value) * (Decimal(self.get_taxes_modifier_display())/100), 2)

    def tag_taxes(self):
        return f'{self.taxes()} {CURRENCY}'

    def tag_paid(self):
        if self.is_paid:
            return format_html('<span class="badge badge-success">Paid</span>')
        return format_html('<span class="badge badge-warning">Not Paid</span>')

    def tag_paid_value(self):
        return '%s %s' % (self.paid_value, CURRENCY)

    tag_paid_value.short_description = 'Αποπληρωμένο Πόσο'

    def tag_cost_value(self):
        return '%s %s' % (self.total_cost, CURRENCY)

    def tag_discount(self):
        return '%s %s' % (self.discount, CURRENCY)

    def tag_voucher_discount(self):
        return f'{self.voucher_discount} {CURRENCY}'

    def tag_shipping_cost(self):
        return f'{self.shipping_method_cost} {CURRENCY}'

    def tag_payment_cost(self):
        return f'{self.payment_cost} {CURRENCY}'

    @property
    def get_total_taxes(self):
        choice = 24
        for ele in TAXES_CHOICES:
            if ele[0] == self.taxes:
                choice = ele[1]
        return self.final_value * (Decimal(choice) / 100)

    @property
    def get_order_items(self):
        return self.order_items.all()

    @property
    def tag_remain_value(self):
        return '%s %s' % (round(self.final_value - self.paid_value, 2), CURRENCY)

    def tag_status(self):
        return f'{self.get_status_display()}'

    def tag_order_type_and_status(self):
        text = f'{self.get_order_type_display()} - {self.get_status_display()}' if self.order_type in ['e',
                                                                                                       'r'] else f'{self.get_order_type_display()}'
        back_color = 'success' if self.order_type in ['e', 'r'] and self.status in ['4', '7',
                                                                                    '8'] else 'info' if self.order_type in [
            'e', 'r'] else 'danger' if self.order_type == 'c' else 'warning'
        return mark_safe('<td class="%s">%s</td>' % (back_color, text))

    def tag_costumer(self):
        return self.profile

    def is_printed(self):
        return 'Printed' if self.printed else 'Not Printed'

    @staticmethod
    def check_voucher_if_used(voucher):
        qs = Order.objects.filter(vouchers=voucher)
        return True if qs.exists() else False

    def create_subs_from_eshop_order(self, cart, user):
        for cart_subscribe in cart.cart_subscribe.all():
            check_if_exists = UserSubscribe.check_active_subscription(user, cart_subscribe.subscribe)
            if not check_if_exists:
                UserSubscribe.objects.create(
                    subscription=cart_subscribe.subscribe,
                    user=user,
                    value=cart_subscribe.value,
                    uses=cart_subscribe.uses
                )
        for cart_subscribe in cart.cart_subscribe.all():
            OrderSubscribe.objects.create(
                subscribe=cart_subscribe.subscribe,
                order_related=self,
                value=cart_subscribe.value,
                cart_related=cart
            )
        qs = OrderSubscribe.objects.filter(order_related=self)
        add_value = qs.aggregate(Sum('value'))['value__sum'] if qs.exists() else 0.00
        self.subscribe_cost = add_value
        self.save()

    def create_sub_discounts_from_eshop_order(self, cart, user):
        for discount_order in cart.cartsubscribediscount_set.all():
            OrderSubscribeDiscount.objects.create(
                order_related=self,
                uses=discount_order.uses,
                total_discount=discount_order.total_discount,

            )

    @staticmethod
    def create_eshop_order(request, cart):
        profile = cart.cart_profile
        email = profile.email
        shipping = cart.shipping_method
        payment_method = cart.payment_method
        user = request.user if request.user.is_authenticated else None
        new_order = Order.objects.create(
            cart_related=cart,
            order_type='e',
            shipping_method=shipping,
            payment_method=payment_method,
            guest_email=email,
        )
        new_order.shipping_method_cost = cart.shipping_method_cost
        new_order.payment_cost = cart.payment_method_cost
        if user:
            new_order.user = user
            new_order.profile = user.profile

        for item in cart.order_items.all():
            OrderItem.create_order_item_from_cart_item(new_order, item)
        new_order.save()
        for voucher in cart.vouchers.all():
            new_order.vouchers.add(voucher)
        new_order.save()
        return new_order

    @staticmethod
    def eshop_orders_filtering(request, queryset):
        search_name = request.GET.get('search_name', None)
        paid_name = request.GET.getlist('paid_name', None)
        printed_name = request.GET.get('printed_name', None)
        status_name = request.GET.getlist('status_name', None)
        payment_name = request.GET.getlist('payment_name', None)
        sell_point_name = request.GET.getlist('sell_point_name', None)
        order_type_name = request.GET.getlist('order_type_name', None)
        order_status_name = request.GET.getlist('order_status_name', None)
        costumer_name = request.GET.getlist('costumer_name', None)
        sort_by = request.GET.get('sort', None)
        queryset = queryset.filter(status__in=order_status_name) if order_status_name else queryset
        queryset = queryset.filter(printed=False) if printed_name else queryset
        queryset = queryset.filter(payment_method__id__in=payment_name) if payment_name else queryset
        queryset = queryset.filter(status__in=status_name) if status_name else queryset
        queryset = queryset.filter(is_paid=False) if paid_name else queryset
        queryset = queryset.filter(order_type__in=order_type_name) if order_type_name else queryset
        queryset = queryset.filter(profile__in=costumer_name) if costumer_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name) |
                                   Q(cellphone__icontains=search_name) |
                                   Q(address__icontains=search_name) |
                                   Q(city__icontains=search_name) |
                                   Q(zip_code__icontains=search_name) |
                                   Q(phone__icontains=search_name) |
                                   Q(first_name__icontains=search_name) |
                                   Q(last_name__icontains=search_name)
                                   ).distinct() if search_name else queryset
        queryset = queryset.filter(seller_account__id__in=sell_point_name) if sell_point_name else queryset
        queryset = queryset.order_by(sort_by) if sort_by else queryset
        return queryset

    @staticmethod
    def filters_data(request, qs):
        date_range = request.GET.get('daterange', None)
        search_name = request.GET.get('search_name', None)
        status_name = request.GET.getlist('status_name', None)
        order_type_name = request.GET.getlist('order_type_name', None)
        date_start, date_end, date_range = clean_date_filter(request, date_range)
        qs = qs.filter(date_expired__range=[date_start, date_end]) if date_range else qs
        qs = qs.filter(order_type__in=order_type_name) if order_type_name else qs
        qs = qs.filter(status__in=status_name) if status_name else qs
        if search_name:
            profiles = Profile.objects.filter(profile_orders__in=qs).distinct()
        return qs

    @staticmethod
    def order_income_type():
        return ['b', 'c', 'wr']

    @staticmethod
    def order_outcome_type():
        return ['r', 'e', 'wa']

    #  django tables
    def table_color(self):
        return 'danger' if self.status == '1' else 'success' if self.status == '8' else 'info'

    def paid_color(self):
        return 'success' if self.is_paid else 'primary'


@receiver(post_save, sender=Order)
def create_unique_number(sender, instance, **kwargs):
    if not instance.number:
        MAX_NUMBERS = 8
        len_num = len(str(instance.id))
        filling_len = MAX_NUMBERS-len_num
        instance.number = filling_len*'0'+ str(instance.id)
        instance.save()
    if instance.profile:
        instance.profile.save()


@receiver(post_save, sender=Order)
def inform_onwer(sender, instance, created, **kwargs):
    print('order signal')
    if created and instance.order_type == 'e':
        print('created')


class OrderItem(DefaultOrderItemModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='Παραστατικό')
    cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    title = models.ForeignKey(Product,
                              on_delete=models.PROTECT,
                              null=True,
                              related_name='retail_items',
                              verbose_name='Προϊόν'
                              )
    #  warehouse_management
    is_find = models.BooleanField(default=False)
    is_return = models.BooleanField(default=False)
    attribute = models.BooleanField(default=False)
    total_value = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text='qty*final_value')
    total_cost_value = models.DecimalField(max_digits=20, decimal_places=0, default=0, help_text='qty*cost')
    broswer = OrderItemManager()
    objects = models.Manager()

    class Meta:
        verbose_name_plural = '2. Προϊόντα Πωληθέντα'
        ordering = ['-order__timestamp', ]
        unique_together = ['title', 'order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._important_fields = ['qty']
        for field in self._important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def old_qty(self):
        for field in self._important_fields:
            orig = '__original_%s' % field
            return getattr(self, orig)

    def __str__(self):
        return self.title.title if self.title else 'Something is wrong'

    def have_attribute(self):
        return self.attribute

    def save(self, *args, **kwargs):
        self.value = self.title.price if self.title else 0
        self.discount_value = self.title.price_discount if self.title else 0
        self.cost = self.title.price_buy if self.title else 0
        self.final_value = self.discount_value if self.discount_value > 0 else self.value
        self.total_value = self.final_value * self.qty
        self.total_cost_value = self.cost * self.qty
        self.attribute = self.have_attr()
        super().save(*args, **kwargs)
        self.title.order_calculations()
        self.order.save()

    def have_attr(self):
        if self.title.have_attr:
            return True
        return False

    def get_clean_value(self):
        return self.final_value * (100 - self.order.taxes / 100)

    @property
    def get_total_value(self):
        return round(self.final_value * self.qty, 2)

    @property
    def get_total_cost_value(self):
        return round(self.cost * self.qty, 2)

    def tag_clean_value(self):
        return '%s %s' % (self.get_clean_value(), CURRENCY)

    def tag_total_value(self):
        return '%s %s' % (self.get_total_value, CURRENCY)

    tag_total_value.short_description = 'Συνολική Αξία'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    tag_final_value.short_description = 'Αξία Μονάδας'

    def tag_value(self):
        return '%s %s' % (self.value, CURRENCY)

    def tag_found(self):
        return 'Found' if self.is_find else 'Not Found'

    def tag_total_taxes(self):
        return '%s %s' % (round(self.value * self.qty * (Decimal(self.order.taxes) / 100), 2), CURRENCY)

    def type_of_order(self):
        return self.order.order_type

    def template_tag_total_price(self):
        return "{0:.2f}".format(round(self.value * self.qty, 2)) + ' %s' % (CURRENCY)

    def price_for_vendor_page(self):
        #  returns silimar def for price in vendor_id page
        return self.value

    def absolute_url_vendor_page(self):
        return reverse('retail_order_section', kwargs={'dk': self.order.id})

    def get_date(self):
        return self.order.date_expired

    def update_warehouse(self):
        instance = self
        product = instance.title
        if not instance.attribute:
            if instance.order.order_type in POSITIVE_ORDER_TYPES:
                product.qty -= instance.qty
            else:
                product.qty += instance.qty
            product.save()

    @staticmethod
    def create_order_item_from_cart_item(order, cart_item):
        instance = OrderItem.objects.create(order=order,
                                            title=cart_item.product,
                                            qty=cart_item.qty,
                                            value=cart_item.value,
                                            discount_value=cart_item.product.price_discount,
                                            cost=cart_item.product.price_buy
                                            )
        if cart_item.product.have_attr:
            OrderItemAttribute.create_objects_from_cart(instance, cart_item)
        for gift in cart_item.cart_item_gift.all():
            OrderGift.create_gift_from_cart(instance, gift)

    @staticmethod
    def create_or_edit_item(order, product, qty, transation_type):
        instance, created = OrderItem.objects.get_or_create(order=order, title=product)
        if transation_type == 'ADD':
            if not created:
                instance.qty += qty
            else:
                instance.qty = qty
                instance.value = product.price
                instance.discount_value = product.price_discount
                instance.cost = product.price_buy
            if product.have_attr:
                OrderItemAttribute.create_objects_from_cart(instance, )
        if transation_type == 'REMOVE':
            instance.qty -= qty
            instance.qty = 1 if instance.qty <= 0 else instance.qty
        instance.save()
        if transation_type == 'DELETE':
            instance.delete()
        order.save()


def create_destroy_title():
    last_order = OrderItem.objects.all().last()
    if last_order:
        number = int(last_order.id) + 1
        return 'ΚΑΤ' + str(number)
    else:
        return 'ΚΑΤ1'


class OrderItemAttribute(models.Model):
    attribute = models.ManyToManyField(Attribute, null=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='attributes')
    qty = models.DecimalField(default=1, decimal_places=2, max_digits=10)
    is_found = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.order_item} - {self.attribute}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order_item.save()

    @staticmethod
    def create_objects_from_cart(order_item, cart_item):
        qs = cart_item.attribute_items.all()
        if qs.exists():
            for cart_attibrute in cart_item.attribute_items.all():
                for attribute in cart_attibrute.attribute.all():
                    new_ = OrderItemAttribute.objects.create(order_item=order_item)
                    new_.attribute.add(attribute)
                    new_.save()


class OrderProfile(models.Model):
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Ονομα')
    last_name = models.CharField(max_length=100, verbose_name='Επιθετο')
    address = models.CharField(max_length=100, verbose_name='Διευθυνση')
    city = models.CharField(max_length=100, verbose_name='Πολη')
    zip_code = models.CharField(max_length=5, verbose_name='Ταχυδρομικος Κωδικας')
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.PROTECT)
    cellphone = models.CharField(max_length=10, verbose_name='Κινητό')
    phone = models.CharField(max_length=10, blank=True, verbose_name='Σταθερο Τηλεφωνο')
    notes = models.TextField(blank=True, verbose_name='Σημειωσεις')
    order_type = models.CharField(max_length=50, choices=ADDRESS_TYPES, default='shipping')
    order_related = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_profiles')

    class Meta:
        unique_together = ['order_related', 'order_type']

    def tag_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def tag_full_address(self):
        return f'{self.address} {self.city} TK..{self.zip_code}'

    def tag_phones(self):
        return f'{self.cellphone} ,{self.phone}'

    @staticmethod
    def create_profile_from_cart(form, order, type='shipping'):
        billing_profile, created = Order.objects.get_or_create(order_related=order, order_type=type)
        billing_profile.email = form.cleaned_data.get('email', 'Error')
        billing_profile.first_name = form.cleaned_data.get('first_name', 'Error')
        billing_profile.last_name = form.cleaned_data.get('last_name', 'Error')
        billing_profile.cellphone = form.cleaned_data.get('cellphone', 'Error')
        billing_profile.zip_code = form.cleaned_data.get('postcode', 'Error')
        billing_profile.address = form.cleaned_data.get('address', 'Error')
        billing_profile.city = form.cleaned_data.get('city', 'Error')
        billing_profile.phone = form.cleaned_data.get('phone', None)
        billing_profile.notes = form.cleaned_data.get('notes', None)
        billing_profile.save()

    @staticmethod
    def create_order_profile(request, order, cart):
        profile = cart.cart_profile
        OrderProfile.objects.create(
            order_related=order,
            order_type='a',
            first_name=profile.first_name,
            last_name=profile.last_name,
            address=profile.address,
            zip_code=profile.zip_code,
            city=profile.city,
            cellphone=profile.cellphone,
            phone=profile.phone,
            email=profile.email,
            notes=profile.notes,
        )


class SendReceipt(models.Model):
    order_related = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_voucher')
    is_sent = models.BooleanField(default=False)
    email = models.EmailField(blank=True)
    shipping_code = models.CharField(max_length=240, blank=True)
    shipping_method = models.ForeignKey(Shipping, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=OrderItemAttribute)
def update_warehouse_on_create_attr(sender, instance, created, **kwargs):
    if created:
        order_item = instance.order_item
        attribute = instance.attribute
        if RETAIL_TRANSCATIONS:
            attribute.save()
        else:
            if MANUAL_RETAIL_TRANSCATIONS:
                if order_item.order.order_type in POSITIVE_ORDER_TYPES:
                    attribute.qty += instance.qty
                else:
                    attribute.qty -= instance.qty
                attribute.save()
        if RETAIL_TRANSCATIONS or MANUAL_RETAIL_TRANSCATIONS:
            order_item.save()


@receiver(post_delete, sender=OrderItemAttribute)
def update_order_item_on_delete(sender, instance, **kwargs):
    order_item = instance.order_item
    attribute = instance.attribute
    if RETAIL_TRANSCATIONS:
        attribute.save()
    else:
        if MANUAL_RETAIL_TRANSCATIONS:
            if order_item.order.order_type in POSITIVE_ORDER_TYPES:
                attribute.qty += instance.qty
            else:
                attribute.qty -= instance.qty
            attribute.save()
    if RETAIL_TRANSCATIONS or MANUAL_RETAIL_TRANSCATIONS:
        order_item.save()


@receiver(post_save, sender=OrderItem)
def update_warehouse_on_create_order_item(sender, instance, created, **kwargs):
    if created:
        product = instance.title
        if RETAIL_TRANSCATIONS:
            product.save()
        else:
            if MANUAL_RETAIL_TRANSCATIONS:
                if not instance.attribute:
                    if instance.order.order_type in POSITIVE_ORDER_TYPES:
                        product.qty -= instance.qty
                    else:
                        product.qty += instance.qty
                    product.save()


@receiver(post_delete, sender=OrderItem)
def update_warehouse(sender, instance, **kwargs):
    product = instance.title
    if RETAIL_TRANSCATIONS:
        product.save()
    else:
        if MANUAL_RETAIL_TRANSCATIONS:
            if not instance.attribute:
                if instance.order.order_type in POSITIVE_ORDER_TYPES:
                    product.qty += instance.qty
                else:
                    product.qty -= instance.qty
                product.save()
    instance.order.save()


class OrderSubscribe(models.Model):
    order_related = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_subscribe')
    subscribe = models.ForeignKey(Subscribe, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(default=0, max_digits=20, decimal_places=2)
    cart_related = models.OneToOneField(CartSubscribe, on_delete=models.SET_NULL, null=True)


class OrderSubscribeDiscount(models.Model):
    order_related = models.ForeignKey(Order, on_delete=models.CASCADE)
    subscription = models.ForeignKey(UserSubscribe, on_delete=models.SET_NULL, null=True)
    total_discount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    uses = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.save(*args, **kwargs)

    @staticmethod
    def check_if_subscription_exists(user):
        sub_exists, sub_qs = UserSubscribe.check_active_subscription(user)
        if sub_exists:
            return True, sub_qs.first()
        return False, None

    @staticmethod
    def check_or_create_subscription(order, subscription):
        value, uses = 0, 0
        remaining_uses = subscription.uses
        products = subscription.subsribe.products.all()
        while remaining_uses > 0:
            for order_item in order.order_items.all():
                if order_item.product in products:
                    value += order_item.total
                    uses += order_item.uses
                    remaining_uses -= order_item.uses
        new_subscribe, created = OrderSubscribeDiscount.objects.create(order_related=order, subscription=subscription)
        new_subscribe.total_discount = value
        new_subscribe.uses = uses
        new_subscribe.save()


@receiver(post_save, sender=OrderSubscribeDiscount)
def update_order_on_sub_create(sender, instance, created, **kwargs):
    if created:
        order = instance.order_related
        order.subscribe_discount_cost = instance.total_discount
        order.save()


class OrderGift(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='gifts')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    cart_gift = models.ForeignKey(CartItemGifts, on_delete=models.CASCADE, null=True)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'Gift {self.order} --> {self.product}'

    @staticmethod
    def create_gift_from_cart(order_item, gift):
        OrderGift.objects.create(order_item=order_item,
                                 order=order_item.order,
                                 product=gift.product,
                                 cart_gift=gift,
                                 qty=order_item.qty

                                 )



