from django.db import models
from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib import messages
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
from catalogue.product_attritubes import Attribute, AttributeClass, AttributeProductClass, AttributeRelated, AttributeTitle
from .subscribe_models import CartSubscribe, CartSubscribeDiscount
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
        self.value = cart_items.aggregate(Sum('total_value'))['total_value__sum'] if cart_items.exists() else 0
        self.voucher_discount = self.discount_from_vouchers()
        self.discount_value = self.calculate_discount_from_subs()
        self.subscribe_value = self.calculate_new_subscribes()
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

    def calculate_new_subscribes(self):
        new_subs = self.cart_subscribe.all()
        return new_subs.aggregate(Sum('value'))['value__sum'] if new_subs.exists() else 0.00

    def calculate_discount_from_subs(self):
        cart_items = self.order_items.all()
        subs = self.cart_subscribe.all()
        user_subs = self.user.my_subscribes.filter(active=True) if self.user else Subscribe.objects.none()
        cart_discounts = self.cartsubscribediscount_set.all()
        cart_discounts.update(total_discount=0, total_uses=0)
        cart_item_id_used = []
        for cart_item in cart_items:
            for user_sub in user_subs:
                have_sub = cart_item.check_if_product_in_user_sub(user_sub)
                if have_sub:
                    qty = cart_item.qty if cart_item.qty <= user_sub.subscription.uses else user_sub.subscription.uses
                    cart_discount, created = CartSubscribeDiscount.objects.get_or_create(
                        cart_related=cart_item.cart,
                        subscribe=user_sub.subscription,
                        cart_type='b',
                    )
                    if created:
                        total_uses = cart_item.qty if cart_item.qty <= user_sub.uses else user_sub.uses
                        cart_discount.total_uses = total_uses
                        cart_discount.total_discount = total_uses*cart_item.final_value
                    else:
                        qty = cart_item.qty + cart_discount.total_uses
                        if qty <= user_sub.uses:
                            cart_discount.total_uses += cart_item.qty
                            cart_discount.total_discount += cart_item.total_value
                        else:
                            difference = user_sub.uses - cart_discount.total_uses
                            cart_discount.total_uses = user_sub.uses
                            cart_discount.total_discount += difference*cart_item.final_value
                    cart_discount.save()
                    cart_item_id_used.append(cart_item.id)

            if not cart_item.id in cart_item_id_used:
                for sub in subs:
                    have_sub = cart_item.check_if_product_in_subscribe(sub)
                    if have_sub:
                        cart_discount, created = CartSubscribeDiscount.objects.get_or_create(
                            cart_related=cart_item.cart,
                            subscribe=sub.subscribe,
                            cart_type='a',
                        )
                        if created:
                            qty = cart_item.qty if cart_item.qty <= sub.subscribe.uses else sub.subscribe.uses
                            cart_discount.qty = qty
                            cart_discount.total_discount = qty*cart_item.final_value
                        else:
                            total_qty = cart_item.qty + cart_discount.total_uses
                            qty = total_qty if total_qty <= sub.subscribe.uses else sub.subscribe.uses
                            if total_qty > sub.subscribe.uses:
                                print('total_qty', total_qty)
                                discount_qty = sub.subscribe.uses - cart_discount.total_uses
                                cart_discount.total_discount += discount_qty*cart_item.final_value
                            else:
                                cart_discount.total_discount += cart_item.total_value
                            cart_discount.total_uses = qty if created else cart_discount.total_uses + qty
                        cart_discount.save()
                        cart_item_id_used.append(cart_item.id)
        discount_subs = self.cartsubscribediscount_set.all()
        total_discount = discount_subs.aggregate(Sum('total_discount'))['total_discount__sum'] if discount_subs.exists() else 0.00
        print('total_discount', total_discount, discount_subs.count())
        return total_discount

    @staticmethod
    def check_and_get_active_subscribe(request, cart):
        user = request.user
        if not user.is_authenticated:
            return False, UserSubscribe.objects.none()
        qs = user.my_subscribes.filter(active=True)
        if qs.exists():
            return True, qs.first()
        if cart.cart_subscribe:
            return True, cart.cart_subscribe
        return False, None

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_discount_value(self):
        return f'{self.discount_value} {CURRENCY}'

    def tag_voucher_discount(self):
        return f'{self.voucher_discount} {CURRENCY}'

    def tag_subscribe_value(self):
        return f'{self.subscribe_value} {CURRENCY}'

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


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    have_attributes = models.BooleanField(default=False)
    extra_value = models.DecimalField(default=0, max_digits=10, decimal_places=2)
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
        self.have_attributes = True if self.product.have_attr else False
        self.extra_value = self.get_extra_value() if self.id else 0
        self.final_value = self.price_discount if self.price_discount > 0 else self.value
        self.final_value += self.extra_value
        self.total_value = self.get_total_value()
        super().save(*args, **kwargs)
        self.cart.save()

    def check_if_product_in_subscribe(self, sub):
        if self.product in sub.subscribe.products.all():
            return True
        return False

    def check_if_product_in_user_sub(self, sub):
        if self.product in sub.subscription.products.all():
            return True
        return False

    def get_delete_frontend_url(self):
        return reverse('delete_from_cart', kwargs={'pk': self.id})

    def get_ajax_change_qty_url(self):
        return reverse('cart:ajax_change_qty', kwargs={'pk': self.id})

    def get_total_value(self):
        return self.qty * self.final_value

    def get_extra_value(self):
        if self.have_attributes:
            attrs = self.attribute_items.all()
            attr_cost = attrs.aggregate(Sum('value'))['value__sum'] if attrs.exists() else 0
            return attr_cost
        return 0

    def tag_value(self):
        return '%s %s' % (round(self.value, 2), CURRENCY)

    def tag_total_value(self):
        return f'{self.total_value} {CURRENCY}'

    def tag_final_value(self):
        return '%s %s' % (self.final_value, CURRENCY)

    def tag_attr(self):
        return self.attribute_item

    @staticmethod
    def copy_cart_item_with_multi_attr(cart, order_item):
        qty = order_item.qty
        product = order_item.title
        cart_item = CartItem.objects.create(cart=cart, product=product, qty=qty)
        CartItemGifts.check_if_gift_exists(cart_item)
        cart_item_attr = CartItemAttribute.objects.create(cart_item=cart_item)
        for attr in order_item.attributes.all():
            for attribute in attr.attribute.all():
                cart_item_attr.attribute.add(attribute)
        cart_item_attr.save()
        result, message = True, f'To προϊόν {product} προστέθηκε με επιτυχία'
        return cart_item, message

    @staticmethod
    def create_cart_item_with_multi_attr(cart, product, request):
        qty = request.POST.get('qty', 1)
        try:
            qty = int(qty)
        except:
            qty = 1
        cart_item = CartItem.objects.create(cart=cart, product=product, qty=qty)
        CartItemGifts.check_if_gift_exists(cart_item)
        cart_item_attr = CartItemAttribute.objects.create(cart_item=cart_item)
        for field in request.POST:
            if 'attr_' in field:
                id = field.split('_')[1]
                attr_class = get_object_or_404(AttributeClass, id=id)
                if attr_class.is_radio_button:
                    attr_id = request.POST.get(field)
                    attr = get_object_or_404(AttributeTitle, id=attr_id)
                    cart_item_attr.attribute.add(attr)
                else:
                    attr_ids = request.POST.getlist(field)
                    for attr in attr_ids:
                        cart_item_attr.attribute.add(attr)
        cart_item_attr.save()
        result, message = True, f'To προϊόν {product} προστέθηκε με επιτυχία'
        return cart_item, message

    @staticmethod
    def copy_order_item(order_item, cart):
        product = order_item.title
        qty = order_item.qty
        if product.have_attr:
            new_cart_item, message = CartItem.create_cart_item_with_multi_attr(cart, product, '')
        else:
            new_cart_item, message = CartItem.create_cart_item(cart, product, qty, None)
        return new_cart_item

    @staticmethod
    def add_product_to_cart(request, cart, product):
        # only for products without attrs
        qty = request.POST.get('qty', 1)
        try:
            qty = int(qty)
        except:
            qty = Decimal(1)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.qty = qty if created else cart_item.qty + qty
        if product.support_transcations:
            if cart_item.qty >= product.qty:
                cart_item.qty = product.qty
                messages.warning(request, f'Προσθέσαμε μόνο {product.qty} τεμάχια στο καλάθι επειδή δε υπάρχει αρκετο υπόλοιπο στο κατάστημα.')
        cart_item.save()
        cart_item.refresh_from_db()
        CartItemGifts.check_if_gift_exists(cart_item)

        return cart_item

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


class CartItemAttribute(models.Model):
    attribute = models.ManyToManyField(AttributeTitle, blank=True,  null=True)
    cart_item = models.ForeignKey(CartItem, on_delete=models.CASCADE, related_name='attribute_items')
    qty = models.IntegerField(default=1)
    value = models.DecimalField(default=0, decimal_places=2, max_digits=10)

    def __str__(self):
        return f'{self.cart_item.product}- {self.cart_item.cart}'

    def save(self, *args, **kwargs):
        self.value = self.get_value() if self.id else 0
        super(CartItemAttribute, self).save()
        self.cart_item.save()

    def get_value(self):
        value = 0
        for ele in self.attribute.all():
            value += ele.value
        return value

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


class CartProfile(models.Model):
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=100, verbose_name='Ονομα', blank=True, null=True)
    last_name = models.CharField(max_length=100, verbose_name='Επιθετο', blank=True, null=True)
    address = models.CharField(max_length=100, verbose_name='Διευθυνση', blank=True, null=True)
    city = models.CharField(max_length=100, verbose_name='Πολη', blank=True, null=True)
    zip_code = models.CharField(max_length=5, verbose_name='Ταχυδρομικος Κωδικας', blank=True, null=True)
    cellphone = models.CharField(max_length=100, verbose_name='Κινητό', blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, verbose_name='Σταθερο Τηλεφωνο')
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

    def save(self, *args, **kwargs):
        if self.cart_item:
            self.qty = self.cart_item.qty
        super(CartItemGifts, self).save(*args, **kwargs)

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



