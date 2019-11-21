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
        product = order_item.item
        new_cart_item = CartItem.add_product_to_cart(request, cart, product)
        new_cart_item.qty = order_item.qty
        new_cart_item.save()
    messages.success(request, 'Τα Προϊόντα Προστέθήκαν')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def create_new_order_from_order(request, pk):
    cart = check_or_create_cart(request)
    order = get_object_or_404(Order, id=pk)
    if order.user != request.user:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def add_order_item_to_cart_view(request, pk):
    instance = get_object_or_404(OrderItem, id=pk, order__user=request.user)
    product = instance.title
    if product.have_attr:
        cart = check_or_create_cart(request)
        cart_item = CartItem.objects.create(cart=cart, product=product, qty=1)
        CartItemGifts.check_if_gift_exists(cart_item)
        cart_item_attr = CartItemAttribute.objects.create(cart_item=cart_item)
        for attr_class in instance.attributes.all():
            for attr_ in attr_class.attribute.all():
                cart_item_attr.attribute.add(attr_)
        cart_item_attr.save()
        messages.success(request, f'Το Προϊόν {product} προστεθηκε στο καλαθι')
    else:
        return redirect(reverse('add_to_cart', product.slug))
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