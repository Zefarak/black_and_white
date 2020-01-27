from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect, reverse, redirect
from django.contrib import messages

from point_of_sale.models import Order, OrderItem
from cart.models import CartItem, CartItemGifts, CartItemAttribute
from cart.tools import check_or_create_cart


@login_required
def order_change_favorite_status_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if order.favorite_order:
        order.favorite_order = False
    else:
        order.favorite_order = True
    order.save()
    messages.success(request, 'Η κατάσταση της παραγγελίας άλλαξε.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def order_change_title_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    title = request.POST.get('title', order.title)
    order.title = title
    order.save()
    messages.success(request, 'Ο τίτλος της παραγγελίας άλλαξε.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_products_from_order_view(request, pk):
    cart = check_or_create_cart(request)
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    for order_item in order.order_items.all():
        product = order_item.title
        new_cart_item = CartItem.add_product_to_cart(request, cart, product)
        new_cart_item.qty = order_item.qty
        new_cart_item.save()
    messages.success(request, 'Τα Προϊόντα Προστέθήκαν')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def create_new_order_from_order(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        messages.warning(request, 'Κατι πηγε λάθος')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    cart = check_or_create_cart(request)
    for cart_item in cart.order_items.all():
        cart_item.delete()
    for order_item in order.order_items.all():
        CartItem.copy_cart_item_with_multi_attr(cart, order_item)
    cart.refresh_from_db()
    cart.active = False
    cart.status = 'Submitted'
    cart.shipping_method = order.shipping_method
    cart.payment_method = order.payment_method
    cart.save()
    cart.refresh_from_db()

    new_eshop_order = Order.create_eshop_order(request, cart)
    new_eshop_order.shipping_method = order.shipping_method
    new_eshop_order.payment_method = order.payment_method
    new_eshop_order.create_subs_from_eshop_order(cart, request.user)
    new_eshop_order.create_sub_discounts_from_eshop_order(cart, request.user)
    new_eshop_order.create_gifts(cart)
    new_eshop_order.save()
    new_eshop_order.refresh_from_db()

    profiles = order.order_profiles.all()
    for profile in profiles:
        profile.pk = None
        profile.order_related = new_eshop_order
        profile.save()
    messages.success(request, f'Η παραγγελία {order.title} αντιγράφηκε και ξαναέγινε. Σας ευχαριστούμε!.')
    return redirect('decide_payment_process')


@login_required
def add_order_item_to_cart_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        messages.warning(request, 'Κατι πηγε λάθος')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    cart = check_or_create_cart(request)
    for order_item in order.order_items.all():
        CartItem.copy_cart_item_with_multi_attr(cart, order_item)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_or_remove_favorite_order_item_view(request, pk):
    order_item = get_object_or_404(OrderItem, id=pk)
    if order_item.order.user != request.user:
        messages.warning(request, 'Κάτι πήγε λάθος')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    order_item.favorite = False if order_item.favorite else True
    order_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
