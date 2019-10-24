from django.urls import path
from .views import (OrderListView, CreateOrderView, OrderUpdateView, delete_order,
                    check_product, add_to_order_with_attr, order_item_edit_with_attr, OrderItemListView,
                    CostumerCreateView, CostumerListView, CostumerUpdateView, delete_costumer_view,
                    CostumerAccountCardView, create_return_order_view
                    )
from .ajax_views import (ajax_order_item, ajax_search_products, ajax_add_product, ajax_costumers_report,
                         ajax_search_costumers, ajax_costumer_order_pay_view, ajax_search_products_for_cart,
                         ajax_add_product_with_attribute, ajax_edit_product_with_attr_view, ajax_order_search_costumer
                         )
from .views_actions import (auto_create_retail_order, done_order_view, quick_pay_costumer_view, create_copy_order,
                            OrderPrintView, CreateCostumerFromOrder, order_change_costumer, ProfileOrderDetailView,
                            create_or_edit_order_voucher_view, order_voucher_manager_view)
from .eshop_views import EshopOrderListView, EshopOrderDetailView, eshop_order_edit_profile, create_user_view, CreateShippingVoucher
from .ajax_eshop_views import ajax_change_status, ajax_find_product, ajax_find_product_attr, ajax_coupon_view
from .autocomplete_widget import ProfileAutoComplete

app_name = 'point_of_sale'

urlpatterns = [
    path('', EshopOrderListView.as_view(), name='home'),
    path('order-list/', OrderListView.as_view(), name='order_list'),
    path('order-create/', CreateOrderView.as_view(), name='order_create'),
    path('order-items-list-view/', OrderItemListView.as_view(), name='order_item_list_view'),
    path('order-detail/<int:pk>/', OrderUpdateView.as_view(), name='order_detail'),
    path('order-detail/<int:pk>/delete/', delete_order, name='delete_order'),
    path('order/check-add/<int:pk>/<int:dk>/', check_product, name='check_add'),
    path('order/add-product-attr/<int:pk>/<int:dk>/', add_to_order_with_attr, name='add_to_order_attr'),
    path('order/edit-order-item-with-att/<int:pk>/', order_item_edit_with_attr, name='edit_order_item_attr'),
    path('copy-order/<int:pk>/', create_copy_order, name='copy_order'),
    path('order/print/<int:pk>/', OrderPrintView.as_view(), name='print_order'),
    path('order/create/costumer/<int:pk>/', CreateCostumerFromOrder.as_view(), name='order_create_costumer'),

    #  ajax calls
    path('order/ajax/edit-order-item/<slug:action>/<int:pk>/', ajax_order_item, name='ajax_order_item_edit'),
    path('ajax/search-items/<int:pk>/', ajax_search_products, name='ajax_search'),
    path('ajax/search-items-cart/<int:pk>/', ajax_search_products_for_cart, name='ajax_search_for_cart'),
    path('ajax/search-items/<int:pk>/<int:dk>/', ajax_add_product, name='ajax_add_product'),
    path('ajax/costumer-pay-order/<int:pk>/', ajax_costumer_order_pay_view, name='ajax_costumer_pay_order'),
    path('ajax/costumer/report', ajax_costumers_report, name='ajax_costumer_report'),
    path('ajax/costumer/search/', ajax_search_costumers, name='ajax_costumer_search'),
    path('ajax/add-product-with-attr/<int:pk>/<int:dk>/<int:ak>/', ajax_add_product_with_attribute,
         name='ajax_add_product_with_attr'),
    path('ajax-p/edit-product-with-attr/<slug:action>/<int:pk>/', ajax_edit_product_with_attr_view,
         name='ajax_edit_product_with_attr'),
    path('ajax/order/costumer/search/<int:pk>/', ajax_order_search_costumer, name='ajax_order_search_costumer'),

    #  actions
    path('action/auto-create-order/<slug:action>/', auto_create_retail_order, name='auto_create_order'),
    path('action/change-costumer/<int:pk>/<int:dk>/', order_change_costumer, name='order_change_costumer'),
    path('action/edit-profile/<int:pk>/', ProfileOrderDetailView.as_view(), name='order_profile_edit'),
    path('action/send-email/<int:pk>/', create_or_edit_order_voucher_view, name='send_order_email'),
    path('action/order/voucher-manager/<int:pk>/', order_voucher_manager_view, name='voucher_manager'),

    path('action/order-done/<int:pk>/<slug:action>/', done_order_view, name='action_order_done'),
    path('autocomplete/profile/', ProfileAutoComplete.as_view(), name='autocomplete_profile'),

    path('create/shipping/voucher/<int:pk>/', CreateShippingVoucher.as_view(), name='create_shipping_voucher'),


    # costumer views
    path('costumer/list/', CostumerListView.as_view(), name='costumer_list_view'),
    path('costumer/create/', CostumerCreateView.as_view(), name='costumer_create_view'),
    path('costumer/detail/<int:pk>/', CostumerUpdateView.as_view(), name='costumer_update_view'),
    path('costumer/delete/<int:pk>/', delete_costumer_view, name='costumer_delete_view'),
    path('costumer/account-card/<int:pk>/', CostumerAccountCardView.as_view(), name='costumer_account_card'),
    path('costumer/quick/pay/<int:pk>/', quick_pay_costumer_view, name='costumer_pay'),

    # eshop views
    path('eshop/views/list/', EshopOrderListView.as_view(), name='eshop_list_view'),
    path('eshop/views/detail/<int:pk>/', EshopOrderDetailView.as_view(), name='eshop_detail_view'),

    # eshop_ajax_views
    path('ajax/eshop/change-status/<int:pk>/', ajax_change_status, name='ajax_change_status'),
    path('ajax/find/product/<int:pk>/', ajax_find_product, name='ajax_find_product'),
    path('profile/edit/<int:pk>/', eshop_order_edit_profile, name='eshop_edit_profile'),
    path('create-user-from-order/<int:pk>/', create_user_view, name='eshop_create_user'),
    path('ajax/find-attr-warehouse/<int:pk>/', ajax_find_product_attr, name='ajax_attr_found'),
    path('ajax/voucher-create/<int:pk>/', ajax_coupon_view, name='ajax_voucher_add')
]