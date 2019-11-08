from django.urls import path

from .views import (SubscribeHomepageView, SubscribeListView, SubscribeCreateView, SubscribeUpdateView,
                    delete_subscribe_view, UserSubscribeListView, UserSubscribeCreateView, UserSubscribeUpdateView,
                    delete_user_subscribe_view, FrontEndSubscribeListView

                    )
from .ajax_views import ajax_add_or_delete_view, ajax_search_products_view

app_name = 'subscribe'


urlpatterns = [
    path('homepage/', SubscribeHomepageView.as_view(), name='homepage'),
    path('συνδρομες/', FrontEndSubscribeListView.as_view(), name='frontend_subscribe_list'),

    path('list-view/', SubscribeListView.as_view(), name='subscribe_list_view'),
    path('create/', SubscribeCreateView.as_view(), name='subscribe_create'),
    path('update/<int:pk>/', SubscribeUpdateView.as_view(), name='subscribe_update'),
    path('delete/<int:pk>/', delete_subscribe_view, name='subscribe_delete_view'),

    path('user/list-view/', UserSubscribeListView.as_view(), name='user_subscribe_list_view'),
    path('user/create/', UserSubscribeCreateView.as_view(), name='user_subscribe_create'),
    path('user/update/<int:pk>/', UserSubscribeUpdateView.as_view(), name='user_subscribe_update'),
    path('user/delete/<int:pk>/', delete_user_subscribe_view, name='user_subscribe_delete_view'),

    path('ajax/search-products/<int:pk>/', ajax_search_products_view, name='ajax_search_products'),
    path('ajax/add-or-delete-product/<int:pk>/<int:dk>/<slug:action>/', ajax_add_or_delete_view, name='ajax_add_delete_product'),


]