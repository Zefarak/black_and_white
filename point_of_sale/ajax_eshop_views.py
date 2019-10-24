from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Order, OrderItem, Attribute, OrderItemAttribute
from voucher.models import Voucher
from .forms import EshopOrderStatusForm



@staff_member_required
def ajax_change_status(request, pk):
    order = get_object_or_404(Order, id=pk)
    new_status = request.GET.get('change_status', order.status)
    print('ajax works', new_status)
    order.status = new_status
    order.save()
    data = dict()
    form = EshopOrderStatusForm(initial={'status': order.status})
    data['result'] = render_to_string(template_name='point_of_sale/ajax/eshop_views/change_status.html',
                                      request=request,
                                      context={
                                          'object': order,
                                          'form': form
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_find_product(request, pk):
    instance = get_object_or_404(OrderItem, id=pk)
    order = instance.order
    if instance.is_find:
        instance.is_find = False
    else:
        instance.is_find = True
    instance.save()
    data = dict()
    data['result'] = render_to_string(template_name='point_of_sale/eshop_views/product_body.html',
                                      request=request,
                                      context={
                                          'object': order
                                      }
                                    )
    return JsonResponse(data)


@staff_member_required
def ajax_find_product_attr(request, pk):
    instance = get_object_or_404(OrderItemAttribute, id=pk)
    if instance.is_found:
        instance.is_found = False
    else:
        instance.is_found = True
    instance.save()
    data = dict()
    order = instance.order_item.order
    data['result'] = render_to_string(template_name='point_of_sale/eshop_views/product_body.html',
                                     request=request,
                                     context={
                                         'object': order
                                     })
    return JsonResponse(data)


@staff_member_required
def ajax_coupon_view(request, pk):
    slug = request.GET.get('slug', None)
    order = get_object_or_404(Order, id=pk)
    coupon = get_object_or_404(Voucher, code=slug.capitalize())
    if coupon:
        is_available, message = coupon.check_if_its_available(order, coupon, order.user)
        if is_available:
            order.vouchers.add(coupon)
            order.save()
    data = dict()
    data['result'] = render_to_string(template_name='point_of_sale/eshop_views/ajax_voucher.html',
                                      request=request,
                                      context={
                                          'object': order,
                                          'coupons': order.vouchers.all()
                                      })
    return JsonResponse(data)
