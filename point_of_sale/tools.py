from django import forms
from django.conf import settings

from catalogue.product_attritubes import Attribute
from .models import Order, OrderGift, OrderSubscribeDiscount, OrderProfile
from subscribe.models import Subscribe, UserSubscribe

from datetime import datetime
from datetime import timedelta


def generate_or_remove_queryset(form, title_list, queryset):
    fields_added = []
    for title in title_list:
        items = queryset.filter(class_related__title__icontains=title)
        if items.exists():
            print(title)
            form.fields[title].queryset = items.first().my_attributes.all()
            fields_added.append(title)
        else:
            form.fields[title] = forms.ModelChoiceField(queryset=Attribute.objects.all(), widget=forms.HiddenInput(), required=False)
    return fields_added


def checkout_process(request, cart, form):
    eshop_order = Order.create_eshop_order(request, cart)
    OrderProfile.create_order_profile(request, eshop_order, cart)
    if cart.cartsubscribe:
        new_subscribe = cart.cartsubscribe
        active_sub = UserSubscribe.check_active_subscription(cart.user)
        if not active_sub:
            user_sub = UserSubscribe.objects.create(
                date_start=datetime.now(),
                date_end=datetime.now() + timedelta(days=new_subscribe.subscribe.uses.uses),
                user=cart.user,
                subscription=new_subscribe.subscribe,
                value=new_subscribe.value,
                uses=new_subscribe.subscribe.uses
            )
            eshop_order.subscribe_cost = new_subscribe.value
            eshop_order.save()
        else:
            user_sub = UserSubscribe.objects.filter(active=True, user=cart.user).first()
        sub_products = user_sub.subscription.products.all()
        value, uses, total_uses = 0, 0, user_sub.uses
        while total_uses > 0:
            for item in cart.order_items.all():
                if item.product in sub_products:
                    if item.qty > total_uses:
                        value += item.total_value
                        uses += item.qty
                        total_uses -= item.qty
                    else:
                        value += total_uses*item.final_value
                        uses += total_uses
                        total_uses = 0
        user_sub.uses = total_uses
        user_sub.save()
        OrderSubscribeDiscount.objects.create(total_discount=value, uses=uses, order_related=eshop_order)


