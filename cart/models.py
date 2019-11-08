from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .managers import CartManager
from .validators import validate_positive_decimal

from site_settings.models import Shipping, PaymentMethod
from site_settings.constants import CURRENCY
from catalogue.models import Product, Gifts
from catalogue.product_attritubes import Attribute, AttributeClass, AttributeProductClass
from voucher.models import Voucher
from decimal import Decimal

from subscribe.models import Subscribe, UserSubscribe

User = get_user_model()


class Cart(models.Model):
    cart_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='Κωδικός')
    active = models.BooleanField(default=True)
    user = models.ForeignKey(User,
                             null=True,
                             blank=True,
                             related_name='carts',
                             on_delete=models.CASCADE,
                             verbose_name='Χρήστης'
                             )
    OPEN, MERGED, SAVED, FROZEN, SUBMITTED = (
        "Open", "Merged", "Saved", "Frozen", "Submitted")
    STATUS_CHOICES = (
        (OPEN, _("Open - currently active")),
        (MERGED, _("Merged - superceded by another basket")),
        (SAVED, _("Saved - for items to be purchased later")),
        (FROZEN, _("Frozen - the basket cannot be modified")),
        (SUBMITTED, _("Submitted")),
    )
    status = models.CharField(
        _("Status"), max_length=128, default=OPEN, choices=STATUS_CHOICES)

    vouchers = models.ManyToManyField(Voucher)
    timestamp = models.DateTimeField(_("Date created"), auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    date_merged = models.DateTimeField(_("Date merged"), null=True, blank=True)
    date_submitted = models.DateTimeField(_("Date submitted"), null=True,
                                          blank=True)
    editable_statuses = (OPEN, SAVED)

    my_query = CartManager()
    objects = models.Manager()

    shipping_method = models.ForeignKey(Shipping,
                                        blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL,
                                        verbose_name='Τρόπος Μεταφοράς')
    payment_method = models.ForeignKey(PaymentMethod,
                                       blank=True,
                                       null=True,
                                       on_delete=models.SET_NULL,
                                       verbose_name='Αντικαταβολή')
    shipping_method_cost = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    payment_method_cost = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)

    # coupon = models.ManyToManyField(Coupons)
    # coupon_discount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    final_value = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name='Αξία')
    value = models.DecimalField(default=0.00,
                                max_digits=10,
                                decimal_places=2,
                                validators=[validate_positive_decimal, ],
                                verbose_name='Αξία Προϊόντων'
                                )
    discount_value = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name='Έκπτωση')
    voucher_discount = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name='Έκπτωση από Κουπόνια')
    subscribe_value = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name='Κοστος Συνδρομης')

    class Meta:
        ordering = ['-id', ]

    def __str__(self):
        return f'Cart {self.id}'

    def save(self, *args, **kwargs):
        cart_items = self.order_items.all()
        self.value = cart_items.aggregate(Sum('total_value'))['total_value__sum'] if cart_items else 0
        self.voucher_discount = self.discount_from_vouchers()
        self.payment_method_cost = 0.00 if not self.payment_method else self.payment_method.estimate_additional_cost(self.value)
        self.shipping_method_cost = 0.00 if not self.shipping_method else self.shipping_method.estimate_additional_cost(self.value)
        self.final_value = Decimal(self.value) - Decimal(self.discount_value) - Decimal(self.voucher_discount)\
                           + Decimal(self.payment_method_cost) + Decimal(self.shipping_method_cost) + Decimal(self.subscribe_value)
        super().save(*args, **kwargs)

    def discount_from_vouchers(self):
        vouchers = self.vouchers.all() if self.id else Voucher.objects.none()
        discount = 0
        cart = self
        if vouchers.exists():
            discount = Voucher.calculate_discount_value(instance=cart, vouchers=vouchers)
        return round(discount, 2)

    def check_and_get_active_subscribe(self):
        qs = self.user.my_subscribes.filter(active=True) if self.user else Subscribe.objects.none()
        return self.user.my_subscribes.filter(active=True).exists(), qs

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_discount_value(self):
        return f'{self.discount_value} {CURRENCY}'

    def tag_voucher_discount(self):
        return f'{self.voucher_discount} {CURRENCY}'

    def get_edit_url(self):
        return reverse('cart:cart_detail', kwargs={'pk': self.id})

    def tag_shipping_method_cost(self):
        return f'{self.shipping_method_cost} {CURRENCY}'

    def tag_payment_method_cost(self):
        return f'{self.payment_method_cost} {CURRENCY}'

    @staticmethod
    def filter_data(request, queryset=None):
        queryset = queryset if queryset else Cart.objects.all()
        search_name = request.GET.get('search_name', None)
        status_name = request.GET.getlist('status_name', None)
        queryset = queryset.filter(status__in=status_name) if status_name else queryset
        queryset = queryset.filter(user__username__contains=search_name) if search_name else queryset
        return queryset

    @staticmethod
    def check_voucher_if_used(voucher):
        qs = Cart.objects.filter(vouchers=voucher)
        return True if qs.exists() else False

'''
@receiver(post_save, sender=Cart)
def calculate_voucher_discount(sender, instance, **kwargs):
    if instance.vouchers.all().exists():
        voucher_discount = 0
        for voucher in instance.vouchers.all():
            voucher_discount += voucher.calculate_discount_value(instance, )
        final_value = Decimal(instance.value) - Decimal(instance.discount_value) - Decimal(instance.voucher_discount)
        Cart.objects.filter(id=instance.id).update(final_value=final_value, voucher_discount=voucher_discount)
'''


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    have_attributes = models.BooleanField(default=False)
    value = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                validators=[validate_positive_decimal,
                                            ])
    price_discount = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                         validators=[validate_positive_decimal, ]
                                         )
    final_value = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                      validators=[validate_positive_decimal, ])
    total_value = models.DecimalField(default=0, decimal_places=2, max_digits=10,
                                      validators=[validate_positive_decimal, ])
    objects = models.Manager()

    def __str__(self):
        return f'{self.cart} - {self.product}'

    def save(self, *args, **kwargs):
        self.final_value = self.price_discount if self.price_discount > 0 else self.value
        self.have_attributes = True if self.product.have_attr else False
        self.qty = self.calculate_qty()
        self.total_value = self.get_total_value()
        super().save(*args, **kwargs)
        self.cart.save()

    def calculate_qty(self):
        if self.have_attributes:
            qs = self.attribute_items.all()
            qty = qs.aggregate(Sum('qty'))['qty__sum'] if qs.exists() else 0
            return qty
        return self.qty

    def get_delete_frontend_url(self):
        return reverse('delete_from_cart', kwargs={'pk': self.id})

    def get_ajax_change_qty_url(self):
        return reverse('cart:ajax_change_qty', kwargs={'pk': self.id})

    def get_total_value(self):
        return self.qty * self.final_value

    def tag_value(self):
        return '%s %s' % (round(self.value, 2), CURRENCY)

    def tag_total_value(self):
        return f'{self.total_value} {CURRENCY}'

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)

    def tag_attr(self):
        return self.attribute_item

    @staticmethod
    def create_cart_item_with_multi_attr(cart, product, request):
        qty = request.POST.get('qty', 1)
        cart_item = CartItem.objects.create(cart=cart, product=product, qty=qty)
        CartItemGifts.check_if_gift_exists(cart_item)
        cart_item_attr = CartItemAttribute.objects.create(cart_item=cart_item)
        for field in request.POST:
            if 'attr_' in field:
                id = field.split('_')[1]
                attr_class = get_object_or_404(AttributeProductClass, id=id)
                if attr_class.class_related.is_radio_button:
                    attr_id = request.POST.get(field)
                    attr = get_object_or_404(Attribute, id=attr_id)
                    cart_item_attr.attribute.add(attr)
                else:
                    attr_ids = request.POST.getlist(field)
                    for attr in attr_ids:
                        cart_item_attr.attribute.add(attr)
        cart_item_attr.save()
        result, message = True, f'To προϊόν {product} προστέθηκε με επιτυχία'
        return cart_item, message


    @staticmethod
    def create_cart_item(cart, product, qty, attribute=None):
        result, message = False, ''
        if product.product_class.is_service or not product.product_class.have_transcations:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cart_item.value = product.price
            cart_item.price_discount = product.price_discount
            cart_item.save()
            result, message = True,  f'To προϊόν {product} προστέθηκε με επιτυχία'
        else:
            if qty > 1:
                return False, 'Δυστυχώς δε υπάρχει αρκετή πόσοτητα.'
            if product.have_attr:
                return CartItemAttribute.create_cart_item(cart, product, qty, attribute)
            else:
                cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
                if not created:
                    result, message = False, 'Δυστυχώς δε υπάρχει αρκετή πόσοτητα.'
                else:
                    cart_item.value = product.price
                    cart_item.price_discount = product.price_discount
                    cart_item.qty = 1
                    cart_item.save()
                    result, message = True, f'To προϊόν {cart_item} με ποσοτητα {qty} προστέθηκε με επιτυχία'
        return result, message


@receiver(post_delete, sender=CartItem)
def update_order_on_delete(sender, instance, *args, **kwargs):
    cart = instance.cart
    for ele in instance.attribute_items.all():
        ele.delete()
    cart.save()


@receiver(post_save, sender=CartItem)
def update_prices_on_create(sender, instance, created, **kwargs):
    if created:
        instance.price_discount = instance.product.price_discount
        instance.value = instance.product.price
        instance.save()


class CartItemAttribute(models.Model):
    attribute = models.ManyToManyField(Attribute, blank=True,  null=True)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='attribute_items')
    qty = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.cart_item.product} - {self.attribute.title}'

    def save(self, *args, **kwargs):
        self.cart_item.calculate_qty()
        super(CartItemAttribute, self).save()
        self.cart_item.save()

    @staticmethod
    def create_cart_item(cart, product, qty, attribute_id):
        attribute = get_object_or_404(Attribute, id=attribute_id)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if created:
            cart_item.price_discount = product.price_discount
            cart_item.value = product.price
        cart_item.save()
        cart_item_attr, created = CartItemAttribute.objects.get_or_create(cart_item=cart_item, attribute=attribute)
        if created:
            cart_item_attr.qty = qty
            cart_item_attr.save()
        else:
            check_qty = attribute.qty - cart_item_attr.qty-qty
            if check_qty <= 0:
                return False, 'Δε υπάρχει αρκετή ποσότητα'
            cart_item_attr.qty += qty
            cart_item_attr.save()
        return True, f'To Προϊόν {cart_item.product} με νούμερο {cart_item_attr.attribute} προστέθηκε με επιτυχία.'


class CartSubscribeDiscount(models.Model):
    # calculates the total discount value if sub exists
    cart_related = models.OneToOneField(Cart, on_delete=models.CASCADE)
    total_uses = models.IntegerField(default=1)
    total_discount = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    @staticmethod
    def check_if_discount_exists(request, cart):
        user = request.user
        if not user.is_authenticated:
            return False, None
        cart_sub = CartSubscribe.objects.filter(cart_related=cart)
        if cart_sub.exists():
            return True, cart_sub.first()
        check_user_sub, sub_qs = UserSubscribe.check_active_subscription(user)
        if check_user_sub:
            return True, sub_qs.first()
        return False, None

    @staticmethod
    def check_or_create_discount(cart, subscribe, remaining_uses):
        products = subscribe.products.all()
        value, uses = 0, 0
        while remaining_uses > 0:
            for cart_item in cart.order_items.all():
                if cart_item.product in products:
                    value += cart_item.total_value
                    uses += cart_item.qty
                    remaining_uses -= cart_item.qty
        new_discount, created = CartSubscribeDiscount.objects.get_or_create(cart_related=cart)
        new_discount.total_uses = uses
        new_discount.total_discount = value
        new_discount.save()
        cart.discount_value = value
        cart.save()

    
class CartSubscribe(models.Model):
    # add to cart a new sub to buy
    cart_related = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='cart_subscribe')
    subscribe = models.ForeignKey(Subscribe, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    def __str__(self):
        return self.subscribe.title

    def save(self, *args, **kwargs):
        self.value = self.subscribe.value
        super().save(*args, **kwargs)
        self.cart_related.subscribe_value = self.value
        self.cart_related.save()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def update_cart(self, cart_item):
        cart = self.cart_related
        subscribe = self.subscribe
        if cart_item.product in subscribe.products.all():
            cart.discount_value += cart_item.final_value
            cart_item.save()

    @staticmethod
    def check_if_user_can_add_subscription(cart, subscribe, user):
        new_sub = None
        if user:
            new_sub = CartSubscribe.objects.create(cart_related=cart, subscribe=subscribe)
        return new_sub


class CartProfile(models.Model):
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Ονομα', blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name='Επιθετο', blank=True, null=True)
    address = models.CharField(max_length=100, verbose_name='Διευθυνση', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Πολη', blank=True, null=True)
    zip_code = models.CharField(max_length=5, verbose_name='Ταχυδρομικος Κωδικας', blank=True, null=True)
    cellphone = models.CharField(max_length=10, verbose_name='Κινητό', blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, verbose_name='Σταθερο Τηλεφωνο')
    notes = models.TextField(blank=True, verbose_name='Σημειωσεις')
    cart_related = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='cart_profile')

    def tag_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @staticmethod
    def create_cart_profile(form, cart):
        cart_profile, created = CartProfile.objects.get_or_create(cart_related=cart)
        cart_profile.email = form.cleaned_data.get('email', 'Error')
        cart_profile.first_name = form.cleaned_data.get('first_name', 'Error')
        cart_profile.last_name = form.cleaned_data.get('last_name', 'Error')
        cart_profile.cellphone = form.cleaned_data.get('cellphone', 'Error')
        cart_profile.zip_code = form.cleaned_data.get('zip_code', 'Error')
        cart_profile.address = form.cleaned_data.get('address', 'Error')
        cart_profile.city = form.cleaned_data.get('city', 'Error')
        cart_profile.phone = form.cleaned_data.get('phone', None)
        cart_profile.notes = form.cleaned_data.get('notes', None)
        cart_profile.save()


class CartItemGifts(models.Model):
    cart_related = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='gifts')
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='cart_item_gift')
    qty = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.product.title

    @staticmethod
    def check_if_gift_exists(cart_item):
        product = cart_item.product
        gift_qs = Gifts.objects.filter(status=True, product_related=product)
        if gift_qs.exists():
            cart = cart_item.cart
            for gift in gift_qs:
                cart_item_gift, created = CartItemGifts.objects.get_or_create(cart_related=cart,
                                                                              cart_item=cart_item,
                                                                              )
                cart_item_gift.product = gift.products_gift
                cart_item_gift.qty = cart_item.qty 
                cart_item_gift.save()



