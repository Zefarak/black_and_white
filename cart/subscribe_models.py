from django.db import models
from django.contrib.auth import get_user_model
from django.contrib import messages
from site_settings.constants import CURRENCY
from subscribe.models import Subscribe, UserSubscribe

User = get_user_model()


class CartSubscribe(models.Model):
    # add to cart a new sub to buy
    cart_related = models.ForeignKey('cart.Cart', on_delete=models.CASCADE, related_name='cart_subscribe')
    subscribe = models.ForeignKey(Subscribe, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        unique_together = ['cart_related', 'subscribe']
        app_label = 'cart'

    def __str__(self):
        return self.subscribe.title

    def save(self, *args, **kwargs):
        self.value = self.subscribe.value
        super().save(*args, **kwargs)
        self.cart_related.save()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    @staticmethod
    def check_and_create_cart_subscribe(request, cart, subscribe):
        user = request.user
        user_subs = UserSubscribe.objects.filter(subscription__category_type=subscribe.category_type, user=user, active=True)
        cart_subs = cart.cart_subscribe.all()
        if user_subs.exists():
            messages.warning(request, 'Χρησιμοποιείται ήδη συνδρομή αυτής της κατηγορίας.')
            return False
        if cart_subs.exists():
            messages.warning(request, 'Έχετε χρησιμοποιήσει συνδρομή αυτής της κατηγορίας στο καλάθι σας.')
            return False
        new_sub = CartSubscribe.objects.create(cart_related=cart, subscribe=subscribe)
        messages.success(request, 'Η συνδρομή προστεθηκε στο καλαθι σας.')
        return True


class CartSubscribeDiscount(models.Model):
    # calculates the total discount value if sub exists
    CART_TYPE_CHOICES = (
        ('a', 'Cart Subscribe'),
        ('b', 'User Subscribe')
    )
    cart_type = models.CharField(max_length=1, choices=CART_TYPE_CHOICES, default='a')
    cart_related = models.ForeignKey('cart.Cart', on_delete=models.CASCADE)
    subscribe = models.ForeignKey(Subscribe, on_delete=models.CASCADE, null=True)
    total_uses = models.IntegerField(default=1)
    total_discount = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    class Meta:
        app_label = 'cart'

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
        cart.save()

