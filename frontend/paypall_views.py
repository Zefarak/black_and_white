from django.shortcuts import get_object_or_404, render, reverse
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from cart.tools import  check_or_create_cart
from point_of_sale.models import Order, OrderProfile

from paypal.standard.forms import PayPalPaymentsForm

BUSSNESS_EMAIL = settings.SITE_EMAIL


def payment_process(request):
    cart = check_or_create_cart(request)
    host = request.get_host()

    paypal_dict = {
        'business': BUSSNESS_EMAIL,
        'amount': f'{cart.final_value}',
        'item_name': f'Cart {cart.id}',
        'invoice': str(cart.id),
        'currency_code': 'EUR',
        'notify_url': f'http://{host}{reverse("paypal-ipn")}',
        'return_url': 'http://{}{}'.format(host, reverse('paypal_done')),
        'cancel_return': 'http://{}{}'.format(host, reverse('paypal_canceled')),
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'paypal_/process.html', {'order':cart, 'form': form})


@csrf_exempt
def payment_done(request):
    cart = check_or_create_cart(request)
    cart_profile = cart.cart_profile
    order = Order.create_eshop_order(request, cart)
    OrderProfile.create_order_profile(request, order, cart)

    send_mail('Καταχώρηση Παραγγελίας no celery',
              f'Η παραγγελία με κωδικο {order.number} καταχωρήθηκε',
              BUSSNESS_EMAIL,
              [cart_profile.email, ],

              )
    order.is_paid= True
    order.paid_value = order.final_value
    order.save()
    cart.active = False
    cart.status = 'Submitted'
    cart.save()
    profile = order.profile
    title = 'Πραγματοποίηση Παραγγελίας'
    payment_progress = True
    del request.session['cart_id']
    return render(request, 'paypal_/done.html', context=locals())


@csrf_exempt
def payment_canceled(request):

    return render(request, 'paypal_/canceled.html')

