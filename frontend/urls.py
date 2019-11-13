from django.conf.urls import url
from django.urls import path ,re_path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap


from .views import HomepageView, BrandListView, CategoryView, ProductView, OfferView, SearchView, BrandDetailView, demo_only_view_restart_session, newsletter_form_view, NewProductsListView
from .user_views import UserDashboardView, login_view, register_view, account_activation_sent, activate, update_profile_view, change_password_view, UserProfileOrderListView, add_product_to_wishlist_view, WishlistListView, fast_login_view, remove_from_wishlist_view,  user_personal_data_view, delete_user_view, pdf_user_data_view, user_subscription_view, user_subscription_detail_view, UserCartItemsView
from .cart_checkout_views import CartPageView, add_product_to_cart, delete_product_from_cart, CheckoutView, order_success_url, OrderDetailView, add_product_with_attr_to_cart, add_voucher_to_cart_view, delete_voucher_from_cart_view, decide_what_to_do_with_order_payment, add_subscribe_to_cart, delete_subscription_view
from .ajax_views import ajax_search_brands, ajax_change_cart_item_qty, ajax_check_voucher, ajax_change_cart_attribute_qty, ajax_add_product_modal, ajax_quick_modal_view, ajax_delete_cart_item, ajax_estimate_costs, ajax_update_cate_shipping_method_view
from .footer_views import ShippingListView, PaymentMethodListView, order_status_form_view, TermsView, ReturnProductPolicyView, CompanyView, ContactView, PersonalDataView
from .action_views import order_change_favorite_status_view, order_change_title_view
from .paypall_views import payment_canceled, payment_done, payment_process
from .sitemaps import StaticViewsSitemap, BrandSitemap, CategorySitemap

sitemaps = {
    'static': StaticViewsSitemap,
    'brands': BrandSitemap,
    'category': CategorySitemap
}

urlpatterns = [
    path('', HomepageView.as_view(), name='homepage'),
    path('αναζήτηση/', SearchView.as_view(), name='search_page'),
    path('προσφορές/', OfferView.as_view(), name='offer_view'),
    path('νέα-προϊόντα/', NewProductsListView.as_view(), name='new_products_view'),
    url(r'^κατηγορία/(?P<slug>[-\w]+)/$', CategoryView.as_view(), name='category_page'),
    path('brands/', BrandListView.as_view(), name='brands_view'),
    path('brand/λεπτομέριες/<slug:slug>/', BrandDetailView.as_view(), name='brand_detail_view'),
    path('cart/', CartPageView.as_view(), name='cart_view'),
    re_path(r'^προϊόν/(?P<slug>[-\w]+)/$', ProductView.as_view(), name='product_view'),
    path('newsletter/form/submit/', newsletter_form_view, name='newsletter_form_view'),


    # cart and checkout_paged
    re_path('^προσθήκη-στο-καλάθι/(?P<slug>[-\w]+)/', add_product_to_cart, name='add_to_cart'),
    url(r'^προσθήκη-στο-καλάθι-με-μεγεθολογιο/(?P<slug>[-\w]+)/$', add_product_with_attr_to_cart, name='add_to_cart_with_attr'),
    
    path('voucher/add/', add_voucher_to_cart_view, name='add_voucher_cart_view'),
    path('voucher/delete/<int:pk>/', delete_voucher_from_cart_view, name='delete_voucher_from_cart'),
    path('διαγραφή-από-το-cart/<int:pk>', delete_product_from_cart, name='delete_from_cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout_view'),
    path('decide-payment', decide_what_to_do_with_order_payment, name='decide_payment_process'),
    path('πραγματοποίηση-παραγγελίας/', order_success_url, name='order_success_url'),

    path('add-subscribe-to-cart/<int:pk>/', add_subscribe_to_cart, name='add_subscribe_to_cart'),
    path('delete-subscribe-from-cart/<int:pk>/', delete_subscription_view, name='delete_subscribe_from_cart'),

    #  user pages
    path('συνδεση/', login_view, name='login'),
    path('fast-login/', fast_login_view, name='fast_login'),
    path('δημιουργια-λογαριασμου/', register_view, name='register_view'),
    path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    path('profile/', UserDashboardView.as_view(), name='user_profile'),
    path('επεξεργασία-προφίλ/', update_profile_view, name='update_profile_view'),
    path('αλλαγή-κωδικού/', change_password_view, name='change_password_view'),
    path('profile/όλες-οι-παραγγελίες/', UserProfileOrderListView.as_view(), name='user_profile_order_list'),
    path('profile/παραγγελια-λεπτομέρειες/<slug:slug>/', OrderDetailView.as_view(), name='frontend_order_detail'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    url(r'^wish-list/add-or-remove/(?P<slug>[-\w]+)/', add_product_to_wishlist_view, name='add_product_wishlist'),
    url(r'^wish-list/remove/(?P<slug>[-\w]+)/', remove_from_wishlist_view, name='remove_product_wishlist'),
    path('wist-list/', WishlistListView.as_view(), name='wishlist'),

    path('subscribe-manager/', user_subscription_view, name='frontend_subscribe'),
    path('subscription-detail-view/<int:pk>/', user_subscription_detail_view, name='subscription_detail_view'),
    path('subscribe-add/<int:pk>/', add_subscribe_to_cart, name='add_sub_to_cart'),
    path('τα-προϊόντα-μου/', UserCartItemsView.as_view(), name='user_cart_items'),

    # footer pages
    path('τρόποι-αποστολής/', ShippingListView.as_view(), name='shipping_list_view'),
    path('τρόποι-πληρωμης/', PaymentMethodListView.as_view(), name='payment_list_view'),
    path('όροι-χρήσης/', TermsView.as_view(), name='terms_rules_view'),
    path('η-εταιρία-μας/', CompanyView.as_view(), name='company_view'),
    path('πολιτική-επιστροφών/', ReturnProductPolicyView.as_view(), name='return_policy_view'),
    path('εξέλιξη-παραγγελίας/', order_status_form_view, name='order_status_form'),
    path('επικοινωνια/', ContactView.as_view(), name='contact_view'),
    path('προσωπικά-δεδομένα/', PersonalDataView.as_view(), name='personal_data_view'),
    path('user/personal-data/', user_personal_data_view, name='user_personal_data'),
    path('user/personal-data/pdf/download/', pdf_user_data_view, name='personal_data_pdf_download'),
    path('user/delete/', delete_user_view, name='delete_user'),


    # ajax urls
    path('ajax/search-brands/', ajax_search_brands, name='ajax_search_brands'),
    path('ajax/cart/modify-order-item/<int:pk>/', ajax_change_cart_item_qty, name='ajax_modify_qty'),
    path('ajax/check-voucher/', ajax_check_voucher, name='ajax_check_voucher'),
    path('ajax/cart-attribute/<int:pk>/', ajax_change_cart_attribute_qty, name='ajax_modify_attribute_qty'),
    url(r'^ajax/add-product-modal/(?P<slug>[-\w]+)/$', ajax_add_product_modal, name='ajax_add_product_modal'),
    url(r'^ajax/quick-product-view/(?P<slug>[-\w]+)/$', ajax_quick_modal_view, name='ajax_quick_modal_view'),
    path('ajax/delete/<int:pk>/<slug:action>/', ajax_delete_cart_item, name='ajax_delete_view'),
    path('ajax/estimate/costs/<slug:action>/', ajax_estimate_costs, name='ajax_estimate_cost'),
    path('ajax/checkout-update-prices/', ajax_update_cate_shipping_method_view, name='ajax_checkout_update_cart'),


    path('delete-session/', demo_only_view_restart_session),

    # actions
    path('order/change-status/<int:pk>/', order_change_favorite_status_view, name='order_change_status'),
    path('order/change-title/<int:pk>/', order_change_title_view, name='order_change_title'),


    #  paypall
    path('paypal_/process/', payment_process, name='paypall_process'),
    path('paypal_/done/', payment_done, name='paypal_done'),
    path('paypal_/canceled/', payment_canceled, name='paypal_canceled'),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')



]






