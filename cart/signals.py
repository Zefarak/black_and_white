from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


from .models import Cart, CartItem, CartProfile
from .subscribe_models import CartSubscribeDiscount, CartSubscribe
from subscribe.models import UserSubscribe


@receiver(post_save, sender=Cart)
def create_cart_profile(sender, instance, created, **kwargs):
    if created:
        cart_profile, created = CartProfile.objects.get_or_create(cart_related=instance)


@receiver(post_save, sender=CartItem)
def calculate_discounts(sender, instance, **kwargs):
    product = instance.product
    # subs = instance.cart_item.


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


@receiver(post_delete, sender=CartSubscribe)
def update_cart_on_subscribe_delete(sender, instance, **kwargs):
    cart = instance.cart_related
    cart.subscribe_value = 0
    cart.save()