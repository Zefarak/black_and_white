from django.db import models
from django.contrib.auth import get_user_model
from django.contrib import messages
from site_settings.constants import CURRENCY
from subscribe.models import Subscribe, UserSubscribe

User = get_user_model()


class OrderSubscribe(models.Model):
    order_related = models.ForeignKey('point_of_sale.Order', on_delete=models.CASCADE, related_name='order_subscribes')
    subscribe = models.ForeignKey(Subscribe, on_delete=models.SET_NULL, null=True)
    value = models.DecimalField(default=0, max_digits=20, decimal_places=2)

    class Meta:
        app_label = 'point_of_sale'
        unique_together = ['order_related', 'subscribe']

    def __str__(self):
        return f'{self.order_related.title} - {self.subscribe.title}'

    def save(self, *args, **kwargs):
        self.value = self.subscribe.value if self.subscribe else self.value
        super(OrderSubscribe, self).save(*args, **kwargs)

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    @staticmethod
    def create_sub_from_cart(cart_subscribe, order):
        OrderSubscribe.objects.create(
            order_related=order,
            subscribe=cart_subscribe.subscribe,

        )
        UserSubscribe.objects.create(
            subscription=cart_subscribe.subscribe,
            user=order.user,
            uses=cart_subscribe.subscribe.uses,
            value=cart_subscribe.value
        )


class OrderSubscribeDiscount(models.Model):
    order_related = models.ForeignKey('point_of_sale.Order', on_delete=models.CASCADE)
    subscribe = models.ForeignKey(Subscribe, on_delete=models.CASCADE, null=True)
    total_uses = models.IntegerField(default=1)
    total_discount = models.DecimalField(default=0, decimal_places=2, max_digits=20)

    class Meta:
        app_label = 'point_of_sale'

    def __str__(self):
        if self.subscribe:
            return f'{self.subscribe.title} ==> Εκπτωση.. {self.total_discount}'
        return 'malakiues'

    @staticmethod
    def create_discount_from_cart(cart_discount, order):
        OrderSubscribeDiscount.objects.create(
            order_related=order,
            subscribe=cart_discount.subscribe,
            total_uses=cart_discount.total_uses,
            total_discount=cart_discount.total_discount
        )

        # update the userSub
        user = order.user
        userSubsqs = UserSubscribe.objects.filter(user=user, subscription=cart_discount.subscribe, active=True)
        sub = userSubsqs.first() if userSubsqs.exists() else None
        if sub:
            sub.uses -= cart_discount.total_uses
            sub.save()

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