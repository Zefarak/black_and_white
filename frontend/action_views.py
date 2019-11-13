from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.contrib import messages

from point_of_sale.models import Order
from cart.models import CartItem
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