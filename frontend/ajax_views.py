from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from catalogue.models import Product
from catalogue.product_attritubes import Attribute
from catalogue.product_details import Brand
from cart.models import CartItem, CartItemAttribute
from cart.tools import check_or_create_cart
from voucher.models import Voucher
from site_settings.models import Shipping, PaymentMethod
from contact.forms import ContactFrontEndForm
from .forms import AskForm


def ajax_search_brands(request):
    data = dict()
    search_name = request.GET.get('search_name', None)
    brands = Brand.objects.filter(active=True)
    object_list = brands.filter(title__startswith=search_name.capitalize()) if search_name else Brand.objects.none()
    print(brands, object_list)
    data['result'] = render_to_string(template_name='frontend/ajax_views/brand_container.html',
                                      request=request,
                                      context={'object_list': object_list[:16]})
    return JsonResponse(data)


def ajax_delete_cart_item(request, pk, action):
    cart = check_or_create_cart(request)
    if action == 'product':
        cart_item = get_object_or_404(CartItem, id=pk)
        if cart == cart_item.cart:
            cart_item.delete()
    if action == 'attr':
        cart_item_attr = get_object_or_404(CartItemAttribute, id=pk)
        if cart_item_attr.cart_item.cart == cart:
            cart_item = cart_item_attr.cart_item
            cart_item_attr.delete()
            cart_item.refresh_from_db()
            if not cart_item.attribute_items.exists():
                cart_item.delete()
    cart.refresh_from_db()
    data = dict()
    data['cart_items_result'] = render_to_string(template_name='frontend/ajax_views/cart_items_container.html',
                                                 request=request,
                                                 context={'cart': cart})
    data['cart_result'] = render_to_string(template_name='frontend/ajax_views/cart_container.html',
                                           request=request,
                                           context={'cart': cart})
    return JsonResponse(data)


def ajax_change_cart_item_qty(request, pk):
    qty = request.GET.get('qty', 1)
    cart_item = get_object_or_404(CartItem, id=pk)
    try:
        qty = int(qty)
    except:
        qty = cart_item.qty
    if qty == 1:
        cart_item.qty = qty
    cart_item.save() if cart_item.qty > 0 else cart_item.delete()
    cart = cart_item.cart
    cart.refresh_from_db()
    data = dict()
    shipping_methods = Shipping.browser.active()
    payment_methods = PaymentMethod.my_query.active_for_site()
    data['cart_items_result'] = render_to_string(template_name='frontend/ajax_views/cart_items_container.html',
                                                 request=request,
                                                 context={'cart': cart,
                                                          })
    data['cart_result'] = render_to_string(template_name='frontend/ajax_views/cart_container.html',
                                           request=request,
                                           context={'cart': cart,
                                                    'shipping_methods': shipping_methods,
                                                    'payment_methods': payment_methods
                                                    })
    return JsonResponse(data)


def ajax_change_cart_attribute_qty(request, pk):
    qty = request.GET.get('qty', None)
    data = dict()
    cart_attribute = get_object_or_404(CartItemAttribute, id=pk)
    cart_attribute.qty = int(qty)
    if cart_attribute.qty <= 0:
        cart_attribute.delete()
    else:
        cart_attribute.save()
    cart = cart_attribute.cart_item.cart
    cart.refresh_from_db()
    shipping_methods = Shipping.browser.active()
    payment_methods = PaymentMethod.my_query.active_for_site()
    data['cart_items_result'] = render_to_string(template_name='frontend/ajax_views/cart_items_container.html',
                                                 request=request,
                                                 context={'cart': cart})
    data['cart_result'] = render_to_string(template_name='frontend/ajax_views/cart_container.html',
                                           request=request,
                                           context={'cart': cart,
                                                    'shipping_methods': shipping_methods,
                                                    'payment_methods': payment_methods
                                                    }
                                           )
    return JsonResponse(data)


def ajax_estimate_costs(request, action):
    pk = request.GET.get('pk', None)
    cart = check_or_create_cart(request)
    if action == 'shipping':
        shipping = get_object_or_404(Shipping, id=pk)
        cart.shipping_method = shipping
        cart.save()
    if action == 'payment':
        payment_method = get_object_or_404(PaymentMethod, id=pk)
        cart.payment_method = payment_method
        cart.save()
    cart.refresh_from_db()
    data = dict()
    shipping_methods = Shipping.browser.active()
    payment_methods = PaymentMethod.my_query.active_for_site()
    data['cart_result'] = render_to_string(template_name='frontend/ajax_views/cart_container.html',
                                           request=request,
                                           context={'cart': cart,
                                                    'shipping_methods': shipping_methods,
                                                    'payment_methods': payment_methods
                                                    }
                                           )
    return JsonResponse(data)


def ajax_check_voucher(request):
    data = dict()
    cart = check_or_create_cart(request)
    code = request.GET.get('voucher', None)
    qs = Voucher.objects.filter(code=code.upper())
    voucher = Voucher.objects.get(code=code.upper()) if qs.exists() else None
    message = ''
    if not voucher:
        message = 'Δε υπάρχει κουπόνι με τον κωδικό που χρησιμοποιήσατε.'
    else:
        is_valid, message = voucher.check_if_its_available(cart, request.user, voucher)
        if is_valid:
            cart.vouchers.add(voucher)
            cart.save()
    cart.refresh_from_db()
    data['cart_result'] = render_to_string(template_name='frontend/ajax_views/cart_container.html',
                                           request=request,
                                           context={
                                               'cart': cart,
                                               'message': message
                                           }
                                           )
    return JsonResponse(data)


def ajax_add_product_modal(request, slug):
    product = get_object_or_404(Product, slug=slug)
    attributes = Attribute.my_query.product_attributes_with_qty(product)
    contact_form = ContactFrontEndForm()
    data = dict()
    data['add_modal'] = render_to_string(template_name='frontend/parts/add_product_modal.html',
                                         request=request,
                                         context={'product': product,
                                                  'attributes': attributes,
                                                  'contact_form': contact_form
                                                  }
                                         )
    return JsonResponse(data)


def ajax_quick_modal_view(request, slug):
    print('here!')
    product = get_object_or_404(Product, slug=slug)
    attributes = Attribute.my_query.product_attributes(product)
    data = dict()
    data['result'] = render_to_string(template_name='frontend/parts/quick_view_modal.html',
                                      request=request,
                                      context={'product': product,
                                               'attributes': attributes
                                            }
                                         )
    return JsonResponse(data)


def ajax_update_cate_shipping_method_view(request):
    cart = check_or_create_cart(request)
    new_shipping_method = request.GET.get('shipping_method', 1)
    shiping_method = get_object_or_404(Shipping, id=new_shipping_method)
    cart.shipping_method = shiping_method
    cart.save()
    data = dict()
    cart.refresh_from_db()
    data['result'] = render_to_string(template_name='frontend/ajax_views/checkout_price_container.html',
                                      request=request,
                                      context={
                                          'cart': cart,
                                          'vouchers': cart.vouchers.all()
                                      }
                                      )
    return JsonResponse(data)
