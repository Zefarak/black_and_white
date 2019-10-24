from django.urls import path

from .views import VoucherListView, voucher_detail_view, VoucherCreateView, voucher_choose_products_view
from .ajax_views import ajax_add_brand_to_voucher, ajax_add_category_to_voucher, ajax_add_or_remove_products, ajax_search_queryset

app_name= 'vouchers'

urlpatterns = [
    path('list/', VoucherListView.as_view(), name='voucher_list'),
    path('create/', VoucherCreateView.as_view(), name='voucher_create'),
    path('detail/<int:pk>/', voucher_detail_view, name='voucher_detail'),
    path('choose/products/<int:pk>/', voucher_choose_products_view, name='voucher_range'),

    #  ajax urls
    path('ajax/category-voucher/<int:pk>/<int:dk>/<slug:action>/', ajax_add_category_to_voucher, name='ajax_voucher_category'),
    path('ajax/brand-voucher/<int:pk>/<int:dk>/<slug:action>/', ajax_add_brand_to_voucher, name='ajax_voucher_brand'),
    path('ajax/products-voucher/<int:pk>/<int:dk>/<slug:action>/', ajax_add_or_remove_products, name='ajax_voucher_product'),
    path('ajax/search-queryset/<int:pk>/', ajax_search_queryset, name='ajax_search_queryset')

]