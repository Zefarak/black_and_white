from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import ChartSize, Product


@staff_member_required
def ajax_chart_size_modify_view(request, pk, dk, action):
    instance = get_object_or_404(ChartSize, id=pk)
    product = get_object_or_404(Product, id=dk)
    if action == 'add':
        previous_instances = product.chartsize_set.all()
        for ele in previous_instances:
            ele.products.remove(product)
            ele.save()
        instance.products.add(product)
        instance.save()
    if action == 'delete':
        instance.products.remove(product)
        instance.save()
    data = dict()
    data['result'] = render_to_string(template_name='chart_size/ajax/ajax_modify_container.html',
                                      request=request,
                                      context={
                                          'object': instance
                                      }
                                      )
    return JsonResponse(data)
