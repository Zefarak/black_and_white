from django.views.generic import TemplateView, DetailView, FormView
from django.shortcuts import get_object_or_404, HttpResponseRedirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import redirect, reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from accounts.models import Profile
from cart.models import CartItem, CartProfile, CartItemGifts
from cart.subscribe_models import  CartSubscribe, CartSubscribeDiscount
from cart.tools import check_or_create_cart, add_product_to_cart_movements
from catalogue.models import Product
from .my_decorators import site_active
from catalogue.product_attritubes import Attribute
from site_settings.models import Shipping, PaymentMethod
from cart.forms import CheckOutForm
from point_of_sale.models import Order, OrderProfile, SendReceipt, OrderSubscribe
from voucher.models import Voucher
from django.views.decorators.cache import cache_control
from subscribe.models import Subscribe, UserSubscribe
from site_settings.models import SiteSettings
BUSSNESS_EMAIL = settings.SITE_EMAIL


class CartPageView(TemplateView):
    template_name = 'frontend/cart_page.html'

    def get_context_data(self, **kwargs):
        context = super(CartPageView, self).get_context_data(**kwargs)
        page_title = 'Καλάθι'
        shipping_methods = Shipping.browser.active()
        payment_methods = PaymentMethod.my_query.active_for_site()
        context.update(locals())
        return context


@login_required
def add_subscribe_to_cart(request, pk):
    site_setting = get_object_or_404(SiteSettings, id=1)
    if not site_setting.is_open:
        messages.warning(request, 'Αυτή την στιγμή το delivery είναι κλείστο. Ελάτε για ένα ποτάκι όμως!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    instance = get_object_or_404(Subscribe, id=pk)
    cart = check_or_create_cart(request)
    check_if_can_add = CartSubscribe.check_and_create_cart_subscribe(request, cart, instance)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@site_active
def add_product_to_cart(request, slug):
    cart = check_or_create_cart(request)
    product = get_object_or_404(Product, slug=slug)
    if product.support_transcations and product.qty <= 0:
        # check if product support transcations and check exist qty
        messages.warning(request, 'Δυστηχώς δε υπάρχει επαρκή ποσότητα')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if product.have_attr:
        # check if product support attributes and cancel the order
        messages.warning(request, 'Κάτι πήγε λάθος!')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    session_id = request.session.get('cart_id')
    check_cart_owner = cart.cart_id == session_id
    if check_cart_owner and product.active:
        # checks again if still the product is active and the user
        CartItem.add_product_to_cart(request, cart, product)
        messages.success(request, f'To Προϊόν {product.title} προστέθηκε επιτιχώς στο καλάθι!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@site_active
def add_product_with_attr_to_cart(request, slug):
    cart = check_or_create_cart(request)
    product = get_object_or_404(Product, slug=slug)
    cart_item, message = CartItem.create_cart_item_with_multi_attr(cart, product, request)
    messages.success(request, message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_product_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, id=pk)
    session_id = request.session.get('cart_id')
    if session_id == cart_item.cart.cart_id:
        cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@site_active
def ajax_change_cart_item_qty(request, pk, action):
    cart_item = get_object_or_404(CartItem, id=pk)
    cart = cart_item.cart
    session_id = request.SESSION.get('cart_id')
    check_cart_owner = cart.cart_id == session_id
    data = dict()
    if check_cart_owner:
        if action == 'add':
            cart_item.qty += 1
        if action == 'minus':
            cart_item.qty -= 1
        cart_item.save()

    data['cart_container'] = render_to_string(template_name='',
                                              request=request,
                                              context={
                                                  'cart': cart
                                              })
    return JsonResponse(data)


@method_decorator(cache_control(no_cache=True, must_revalidate=True), name='dispatch')
class CheckoutView(FormView):
    form_class = CheckOutForm
    template_name = 'frontend/checkout.html'
    success_url = reverse_lazy('decide_payment_process')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['profiles'] = self.request.user.profile.all()
        return context

    def get(self, request, *args, **kwargs):
        cart = check_or_create_cart(self.request)
        if not cart.order_items.exists():
            messages.warning(self.request, 'Πρεπει να προσθεσετε Προϊόντα για να παραγγειλετε!')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
        return super(CheckoutView, self).get(request, *args, **kwargs)

    def get_initial(self):
        initial = super(CheckoutView, self).get_initial()
        cart = self.cart = check_or_create_cart(self.request)
        user = self.request.user
        if user.is_authenticated:
            profiles = user.profile.filter(user_favorite=True)
            if profiles.exists():
                profile = profiles.first()
                initial['first_name'] = profile.first_name
                initial['last_name'] = profile.last_name
                initial['email'] = user.email
                initial['address'] = profile.shipping_address

                initial['cellphone'] = profile.cellphone
                initial['phone'] = profile.phone
        '''
        if CartProfile.objects.filter(cart_related=cart).exists():
            cart_profile = cart.cart_profile
            initial['first_name'] = cart_profile.first_name
            initial['last_name'] = cart_profile.last_name
            initial['email'] = cart_profile.email
            initial['address'] = cart_profile.address
            initial['city'] = cart_profile.city
            initial['zip_code'] = cart_profile.zip_code
            initial['cellphone'] = cart_profile.cellphone
            initial['phone'] = cart_profile.phone
        '''
        initial['shipping_method'] = cart.shipping_method
        initial['payment_method'] = cart.payment_method
        initial['city'] = 'Μολαοι'
        initial['zip_code'] = 23052
        return initial

    def form_valid(self, form):
        # checks if checkout form is valid
        shipping_method = form.cleaned_data['shipping_method']
        payment_method = form.cleaned_data['payment_method']
        cart = check_or_create_cart(self.request)
        cart.shipping_method = shipping_method
        cart.payment_method = payment_method
        cart.save()
        if cart.order_items.count() <= 0:
            messages.warning(self.request, 'Δε έχετε Προϊόντα στο καλάθι')
            return super(CheckoutView, self).form_valid(form)
        CartProfile.create_cart_profile(form, cart)
        # now we check if the payment type is a service, If its a service we dont create the order now
        # because something can go bad, so will created to success url
        if payment_method.payment_type in ['c', 'd']:
            return super(CheckoutView, self).form_valid(form)
        # if the payment_method is a regular payment type we continue the order process
        cart.active = False
        cart.status = 'Submitted'
        cart.save()
        cart.refresh_from_db()
        
        self.new_eshop_order = Order.create_eshop_order(self.request, cart)
        self.new_eshop_order.create_subs_from_eshop_order(cart, self.request.user)
        self.new_eshop_order.create_sub_discounts_from_eshop_order(cart, self.request.user)
        self.new_eshop_order.create_gifts(cart)
        OrderProfile.create_order_profile(self.request, self.new_eshop_order, cart)
        self.new_eshop_order.save()
        self.new_eshop_order.refresh_from_db()
        email = form.cleaned_data.get('email')
        send_mail('Καταχώρηση Παραγγελίας',
                  f'Σας ευχαριστούμε που μας προτιμήσατε! Η παραγγελία σας με κωδικο'
                  f' {self.new_eshop_order.number} καταχωρήθηκε',
                  BUSSNESS_EMAIL,
                  [email, ],

                  )
        send_mail('Έχετε νέα Παραγγελία',
                  f'Ημερομηνια.. {self.new_eshop_order.date_expired} |'
                  f' {self.new_eshop_order.guest_email} | Ποσο {self.new_eshop_order.tag_final_value()}',
                  BUSSNESS_EMAIL,
                  [BUSSNESS_EMAIL, ]
                  )

        return super(CheckoutView, self).form_valid(form)


@login_required
def change_profile_from_checkout_view(request):
    pk = request.GET.get('select_', None)
    instance = get_object_or_404(Profile, id=pk)
    if instance.user != request.user:
        messages.warning(request, 'Κατι πήγε λάθος')
    else:
        instance.user_favorite = True
        instance.save()
    return HttpResponseRedirect(reverse('checkout_view'))


def decide_what_to_do_with_order_payment(request):
    cart = check_or_create_cart(request)
    payment_method = cart.payment_method
    if payment_method.payment_type in ['a', 'b']:
        return redirect(reverse('order_success_url'))
    if payment_method.payment_type in ['c', 'd']:
        if payment_method.title == 'Paypal':
            return redirect(reverse('paypall_process'))
    return redirect(reverse('order_success_url'))


def order_success_url(request):
    cart = check_or_create_cart(request)
    order = get_object_or_404(Order, cart_related=cart)
    show_bank_div = True if order.payment_method.payment_type == 'b' else False
    title = 'Πραγματοποίηση Παραγγελίας'
    profile = order.order_profiles.first() if order.order_profiles.exists() else None
    del request.session['cart_id']
    return render(request, 'frontend/checkout_success.html', {'order': order,
                                                              'profile': profile,
                                                              'title': title,
                                                              'show_bank_div': show_bank_div,
                                                              'success_order': True
                                                              }
                  )


class OrderDetailView(DetailView):
    model = Order
    template_name = 'frontend/checkout_success.html'
    slug_field = 'number'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        title = f'Παραγγελία {self.object.number}'
        order = self.object
        profile = self.object.order_profiles.first() if self.object.order_profiles.exists() else None
        shipping_voucher = SendReceipt.objects.get(order_related=order) \
            if SendReceipt.objects.filter(order_related=order).exists() else None
        context.update(locals())
        return context


def add_voucher_to_cart_view(request):
    code = request.GET.get('voucher_code', None)
    if not code:
        messages.warning(request, 'Πληκτρολογήστε κωδικό κουπονιού')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if isinstance(code, str):
        code = str(code).upper()
    voucher_exists = Voucher.objects.filter(code=code.upper())
    voucher = voucher_exists.first() if voucher_exists.exists() else None
    if not voucher:
        messages.warning(request, 'Δε υπάρχει κουπόνι με αυτόν τον κωδικό')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    cart = check_or_create_cart(request)
    is_available, message = voucher.check_if_its_available(cart, request.user, voucher)
    messages.success(request, message)
    if is_available:
        cart.vouchers.add(voucher)
        cart.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def delete_voucher_from_cart_view(request, pk):
    cart = check_or_create_cart(request)
    voucher = get_object_or_404(Voucher, id=pk)
    cart.vouchers.remove(voucher)
    cart.save()
    messages.warning(request, 'Το Κουπόνι αφαιρέθηκε από το καλάθι σας')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required()
def delete_subscription_view(request, pk):
    instance = get_object_or_404(CartSubscribe, id=pk)
    cart = check_or_create_cart(request)
    if not request.user == instance.cart_related.user:
        messages.warning(request, 'Κατι πήγε λάθος')
    else:
        instance.delete()
        messages.success(request, 'Η συνδρομη αφαιρεθηκε από το καλάθι.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
