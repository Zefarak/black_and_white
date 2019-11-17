from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import *


@receiver(post_save, sender=CartItem)
def check_gifts_on_creation(sender, instance, created, **kwargs):
    if created:
        pass


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


@receiver(post_save, sender=OrderSubscribeDiscount)
def update_order_on_sub_create(sender, instance, created, **kwargs):
    if created:
        order = instance.order_related
        order.subscribe_discount_cost = instance.total_discount
        order.save()
