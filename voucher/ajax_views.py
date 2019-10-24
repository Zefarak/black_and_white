from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django_tables2 import RequestConfig

from catalogue.categories import Category
from catalogue.product_details import Brand
from catalogue.models import Product
from .models import ProductRange, Voucher
from .tables import CategorySelectedDataTable, BrandSelectedDataTable, ProductSelectedDataTable, VoucherProductForSelectTable, VoucherCategoryTable, VoucherBrandTable


@staff_member_required
def ajax_add_category_to_voucher(request, pk, dk, action):
    category = get_object_or_404(Category, id=dk)
    product_range = get_object_or_404(ProductRange, id=pk)
    data = dict()
    if action == 'add':
        product_range.included_categories.add(category)
    elif action == 'delete':
        product_range.included_categories.remove(category)
    product_range.save()

    voucher = product_range.voucher
    product_range.refresh_from_db()
    selected_table = CategorySelectedDataTable(product_range.included_categories.all())
    RequestConfig(request).configure(selected_table)
    data['result'] = render_to_string(request=request,
                                      template_name='voucher/ajax/selected_data.html',
                                      context={
                                          'voucher': voucher,
                                          'selected_table': selected_table
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_add_brand_to_voucher(request, pk, dk, action):
    brand = get_object_or_404(Brand, id=dk)
    product_range = get_object_or_404(ProductRange, id=pk)
    if action == 'add':
        product_range.included_brands.add(brand)
    if action == 'delete':
        product_range.included_brands.remove(brand)
    product_range.save()
    product_range.refresh_from_db()
    voucher = product_range.voucher
    selected_table = BrandSelectedDataTable(product_range.included_brands.all())
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='voucher/ajax/selected_data.html',
                                      context={
                                          'voucher': voucher,
                                          'selected_table': selected_table
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_add_or_remove_products(request, pk, dk, action):
    product_range = get_object_or_404(ProductRange, id=pk)
    product = get_object_or_404(Product, id=pk)

    if action == 'add':
        product_range.included_products.add(product)
    elif action == 'delete':
        product_range.included_products.remove(product)
    product_range.save()
    product_range.refresh_from_db()
    data = dict()
    selected_data = ProductSelectedDataTable(product_range.included_products.all())
    data['result'] = render_to_string(template_name='voucher/ajax/selected_data.html',
                                      request=request,
                                      context={
                                          'voucher': product_range.voucher,
                                          'selected_data': selected_data
                                      }
                                      )
    return JsonResponse(data)


@staff_member_required
def ajax_search_queryset(request, pk):
    q = request.GET.get('q', None)
    voucher = get_object_or_404(Voucher, id=pk)
    rule_type = voucher.voucher_rule.offer_type
    products = Product.objects.none()
    queryset_table = VoucherProductForSelectTable(products)
    if rule_type == 'Category':
        print('Works!')
        categories = Category.objects.filter(name__startswith=q.capitalize()) if q else Category.objects.filter(active=True)
        queryset_table = VoucherCategoryTable(categories)
    if rule_type == 'Brand':
        brands = Brand.objects.filter(title=q.capitalize()) if q else Brand.objects.filter(active=True)
        queryset_table = VoucherBrandTable(brands)
    RequestConfig(request).configure(queryset_table)
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='voucher/ajax/result_data.html',
                                      context={
                                          'queryset_table': queryset_table,
                                          'voucher': voucher
                                      }
                                    )
    return JsonResponse(data)

