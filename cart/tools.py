from django.shortcuts import redirect, reverse
from string import ascii_letters
from .models import Cart, CartItem, CartItemGifts, CartSubscribeDiscount, CartSubscribe
import random
from decimal import Decimal


def generate_cart_id():
    new_id = ''
    for i in range(50):
        new_id = new_id + random.choice(ascii_letters)
    return new_id


def check_if_cart_id(request):
    cart_id = request.session.get('cart_id', None)
    if cart_id is None:
        request.session['cart_id'] = generate_cart_id()
    return request.session['cart_id']


def check_or_create_cart(request):
    user = request.user
    cart_id = check_if_cart_id(request)
    cart, created = Cart.objects.get_or_create(cart_id=cart_id)
    if created and user.is_authenticated:
        cart.user = user
        cart.save()
    return cart


def check_cart_if_exists_for_context_processor(request):
    cart_id = check_if_cart_id(request)
    qs = Cart.objects.filter(cart_id=cart_id)
    if qs.exists():
        return check_or_create_cart(request)
    return False


def add_to_cart_with_attr(product):
    return redirect(reverse('product_view', kwargs={'slug': product.slug}))


def add_to_cart(request, product):
    cart = check_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)
    if created:
        cart_item.qty = 1
        cart_item.value = product.price
        cart_item.price_discount = product.price_discount
    else:
        cart_item.qty += 1
    cart_item.save()


def remove_from_cart_with_attr():
    print('delete')


def add_product_to_cart_movements(request, cart, product):
    qty = request.POST.get('qty', 1)
    try:
        qty = int(qty)
    except:
        qty=Decimal(1)
    print(qty)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.qty = qty if created else cart_item.qty + qty
    cart_item.save()
    cart_item.refresh_from_db()
    # all steps needed for create or edit a cart_item
    # after the creation of the cart we check if there is any gifts
    CartItemGifts.check_if_gift_exists(cart_item)
    # next move is to check if user have or added a subscription
    '''
    check_if_sub_exists, subscribe = CartSubscribeDiscount.check_if_discount_exists(request, cart)
    if check_if_sub_exists:
        CartSubscribeDiscount.check_or_create_discount(cart, subscribe, subscribe.uses)
    '''


