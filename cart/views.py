from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from catalogue.models import Product
from .models import CartItem, Cart
from point_of_sale.models import Order
from .forms import CartForm

from .tables import CartTable, ProductCartTable, CartItemTable
from .tools import add_to_cart, add_to_cart_with_attr, remove_from_cart_with_attr
from point_of_sale.models import OrderItem, Order
from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class CartListView(ListView):
    model = Cart
    template_name = 'cart/listview.html'

    def get_queryset(self):
        queryset = Cart.filter_data(self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_title, back_url = 'Καλάθια', reverse('point_of_sale:home')
        queryset_table = CartTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        # filters
        search_filter = [True]*1
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CartUpdateView(DetailView):
    model = Cart
    template_name = 'cart/detail_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url = self.request.GET.get('back_url', reverse('cart:cart_list'))
        order = Order.objects.filter(cart_related=self.object).first() if Order.objects.filter(cart_related=self.object).exists() else None
        context.update(locals())
        return context


def check_cart_movement(request, pk, action):
    if action == 'add':
        product = get_object_or_404(Product, id=pk)
        add_to_cart_with_attr(product) if product.have_attr else add_to_cart(request, product)
        messages.success(request, f'{product} added to the cart.')
    if action == 'remove':
        cart_item = get_object_or_404(CartItem, id=pk)
        remove_from_cart_with_attr() if cart_item.have_attributes else cart_item.delete()
        messages.warning(request, f'{cart_item} is deleted.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def ajax_cart_change_qty(request, pk):
    instance = get_object_or_404(CartItem, id=pk)
    new_qty = request.GET.get('qty', 1)
    new_qty = int(new_qty)
    instance.qty = new_qty
    instance.save()
    instance.refresh_from_db()
    cart = instance.cart
    cart.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='cart/ajax_cart_container.html',
                                      request=request,
                                      context={'cart': cart})
    return JsonResponse(data)


@staff_member_required
def create_order_from_cart_view(request, pk):
    cart = get_object_or_404(Cart, id=pk)
    order, created = Order.objects.get_or_create(cart_related=cart)
    order.order_type = 'e'
    order.save()
    if created:
        for ele in cart.order_items.all():
            OrderItem.objects.create(title=ele.product,
                                     order=order,
                                     qty=ele.qty,
                                     value=ele.value,
                                     )
        return redirect(order.get_edit_url())
    else:
        messages.warning(request, 'Υπάρχει Παραστατικό σε αυτό το Cart')
    return redirect(cart.get_edit_url())


