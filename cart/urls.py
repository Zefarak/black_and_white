from django.urls import path
from .views import CartListView, CartUpdateView, check_cart_movement, ajax_cart_change_qty, create_order_from_cart_view
from .ajax_views import ajax_search_products_for_cart, ajax_order_item, ajax_add_product

app_name = 'cart'

urlpatterns = [
    #  dashboard urls
    path('list/', CartListView.as_view(), name='cart_list'),
    path('detail/<int:pk>/', CartUpdateView.as_view(), name='cart_detail'),

    path('check/<int:pk>/<slug:action>/', check_cart_movement, name='check'),
    path('ajax/change-qty/<int:pk>/', ajax_cart_change_qty, name='ajax_change_qty'),
    path('create-order-from-cart/<int:pk>/', create_order_from_cart_view, name='create_order_from_cart'),


    #  ajax calls
    path('order/ajax/edit-order-item/<slug:action>/<int:pk>/', ajax_order_item, name='ajax_order_item_edit'),
    path('ajax/search-items-cart/<int:pk>/', ajax_search_products_for_cart, name='ajax_search_for_cart'),
    path('ajax/search-items/<int:pk>/<int:dk>/', ajax_add_product, name='ajax_add_product'),


    ]