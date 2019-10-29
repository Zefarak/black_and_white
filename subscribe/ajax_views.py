from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from .models import Subscribe
from catalogue.models import Product


@staff_member_required
def ajax_search_products_view(request, pk):
    q = request.GET.get('search_name', None)
    instance = get_object_or_404(Subscribe, id=pk)
    qs = Product.objects.none()
    print('q', q)
    if len(q) > 2:
        qs = Product.filters_data(request, Product.my_query.active())
        print('new qs', qs.count())
    data = dict()
    data['result'] = render_to_string(template_name='subscribe/ajax_views/search_container.html',
                                      request=request,
                                      context={
                                          'qs': qs,
                                          'object': instance
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_add_or_delete_view(request, pk, dk, action):
    print('here')
    instance = get_object_or_404(Subscribe, id=pk)
    product = get_object_or_404(Product, id=dk)
    if action == 'add':
        instance.products.add(product)
    elif action == 'remove':
        instance.products.remove(product)
    instance.save()
    instance.refresh_from_db()
    data = dict()
    data['result'] = render_to_string(template_name='subscribe/ajax_views/selected_data.html',
                                      request=request,
                                      context={
                                          'object': instance
                                      })
    return JsonResponse(data)
