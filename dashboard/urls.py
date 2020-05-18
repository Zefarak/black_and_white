from django.contrib import admin
from django.urls import path, include, re_path

from .views import (DashBoard, ProductsListView, ProductCreateView,
                    product_detail, CategorySiteManagerView, ProductMultipleImagesView, CharacteristicsManagerView,
                    delete_product, copy_product_view, product_report_view, ProductDiscountView,
                    ProductDiscountCreateView,
                    ProductDiscountUpdateView, ProductCharacteristicCreateView, ProductAttributeManagerView,
                    create_attr_product_class,
                    ProductAttriClassManagerView, RelatedProductsView, product_characteristic_delete_view,
                    WarehouseCategoryCreateView, WarehouseCategoryListView, WarehouseCategoryUpdateView,
                    warehouse_category_delete, delete_product_attribute_view, ProductWithDifferentColorListView,
                    GiftListView, GiftCreateView, GiftUpdateView, delete_gift_view, QuickChangeProductWithQtyView
                    )

from .settings_view import (ProductClassView, ProductClassCreateView,
                            CategorySiteListView, CategorySiteEditView, CategorySiteCreateView, delete_category_site,
                            BrandListView, BrandEditView, BrandCreateView, delete_brand,
                            CharacteristicsListView, characteristics_detail_view, CharacterCreateView,
                            characteristic_delete_view, CharValueEditView, delete_char_value_view,
                            AttributeClassListView, attribute_class_edit_view, attribute_class_delete_view,
                            AttributeClassCreateView, attribute_title_delete_view, AttributeTitleEditView,
                            ColorCreateView, ColorListView, ColorUpdateView, color_delete_view, attribute_class_manager_view,
                            AttributeRelatedCreateView, AttributeRelatedListView, AttributeRelatedUpdateView, attribute_related_delete_view
                            )
from .dashboard_actions import copy_product_view, add_gift_action_view, reset_qty_to_products_view, change_site_setting_status_view
from .ajax_views import (ajax_category_site, ajax_product_images, ajax_add_or_delete_attribute,
                         ajax_change_qty_on_attribute, ajax_products_discount_add, ajax_product_discount_delete,
                         popup_category, popup_brand, popup_vendor, popup_color,ajax_different_color_product_view,
                         ajax_product_calculate_view, ajax_related_products_view, ajax_modify_gift_view, ajax_attribute_show_or_hide,
                         ajax_quick_change_qty_to_product,
                         )
app_name = 'dashboard'


urlpatterns = [
    path('', DashBoard.as_view(), name='home'),
    path('products/', ProductsListView.as_view(), name='products'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/detail/<int:pk>/', product_detail, name='product_detail'),
    path('product/delete/<int:pk>/', delete_product, name='product_delete'),
    path('product/category-site-manager/<int:pk>/', CategorySiteManagerView.as_view(), name='category_manager_view'),
    path('add-multiply-images/<int:pk>/', ProductMultipleImagesView.as_view(), name='image_manager_view'),
    path('product/create-copy/<int:pk>/', copy_product_view, name='create_copy_product'),
    path('product/report/<int:pk>/', product_report_view, name='product_report'),

    path('discount-manager/', ProductDiscountView.as_view(), name='discount_manager'),
    path('discount-manager/create/', ProductDiscountCreateView.as_view(), name='discount_manager_create'),
    path('discount-manager/update/<int:pk>/', ProductDiscountUpdateView.as_view(), name='discount_manager_update'),

    #  popups
    path('product/popups/create-category/', popup_category, name='popup_category'),
    path('product/popups/create-brand/', popup_brand, name='popup_brand'),
    path('product/popups/create-vendor/', popup_vendor, name='popup_vendor'),
    path('product/popups/create-color/', popup_color, name='popup_color'),

    # actions
    path('products/copy/<int:pk>/',copy_product_view, name='copy_product'),

    path('product/characteristic-manager/<int:pk>/', CharacteristicsManagerView.as_view(), name='char_manager_view'),
    path('product/chara-create/<int:pk>/<int:dk>/', ProductCharacteristicCreateView.as_view(), name='product_char_create_view'),

    path('product/attribute-manager/<int:pk>/', ProductAttributeManagerView.as_view(), name='attribute_manager_view'),
    path('product/attribute-create/<int:pk>/<int:dk>/', create_attr_product_class, name='product_create_attr_view'),
    path('product/attribute-detail/<int:pk>/', ProductAttriClassManagerView.as_view(), name='product_attr_detail_view'),
    path('product/attribute-delete/<int:pk>/', delete_product_attribute_view, name='delete_product_attr'),

    path('product/related/<int:pk>/', RelatedProductsView.as_view(), name='related_products_manager_view'),
    path('product/different-color/<int:pk>/', ProductWithDifferentColorListView.as_view(), name='different_color_manager_view'),

    # ajax
    path('ajax/product/analysis/', ajax_product_calculate_view, name='ajax_product_analysis'),
    path('ajax/category-site-manager/<slug:slug>/<int:pk>/<int:dk>/', ajax_category_site, name='ajax_category_site'),
    path('ajax/related-product-manager/<slug:slug>/<int:pk>/<int:dk>/', ajax_related_products_view, name='ajax_related_product'),
    path('ajax/different-color-manager/<slug:slug>/<int:pk>/<int:dk>/', ajax_different_color_product_view,
         name='ajax_different_color_view'),
    path('ajax/image-manager/<slug:slug>/<int:pk>/<int:dk>/', ajax_product_images, name='ajax_image'),
    path('ajax/add-or-delete-attr/<slug:slug>/<int:pk>/<int:dk>/', ajax_add_or_delete_attribute, name='ajax_manage_attribute'),
    path('ajax/add-qty/<int:pk>/', ajax_change_qty_on_attribute, name='ajax_manage_qty_attribute'),
    path('ajax/discount/add-products/<int:pk>/', ajax_products_discount_add, name='ajax_products_discount_add'),
    path('ajax/discount/delete-product/<int:pk>/<int:dk>/', ajax_product_discount_delete, name='ajax_products_discount_delete'),
    path('ajax-modify-gift/<int:pk>/<int:dk>/<slug:action>/', ajax_modify_gift_view, name='ajax_modify_gift'),
    path('ajax/add-or-hide-attr/<int:pk>/', ajax_attribute_show_or_hide, name='ajax_show_or_hide_attr'),


    path('product/characteristic-manager/<int:pk>/', CharacteristicsManagerView.as_view(), name='char_manager_view'),
    path('product/char/delete/<int:pk>/', product_characteristic_delete_view, name='product_char_delete_view'),

    path('product-class-list/', ProductClassView.as_view(), name='product_class_view'),
    path('products-class-create/', ProductClassCreateView.as_view(), name='product_class_create_view'),

    path('category-list/', CategorySiteListView.as_view(), name='category_list'),
    path('category-edit/<int:pk>/', CategorySiteEditView.as_view(), name='category_edit_view'),
    path('category-create/', CategorySiteCreateView.as_view(), name='category_create_view'),
    path('category-delete/<int:pk>/', delete_category_site, name='delete_category_site'),

    path('brand-list/', BrandListView.as_view(), name='brand_list_view'),
    path('brand-edit/<int:pk>/', BrandEditView.as_view(), name='brand_edit_view'),
    path('brand-create/', BrandCreateView.as_view(), name='brand_create_view'),
    path('brand-delete/<int:pk>/', delete_brand, name='delete_brand'),

    path('color-list/', ColorListView.as_view(), name='color_list_view'),
    path('color-edit/<int:pk>/', ColorUpdateView.as_view(), name='color_edit_view'),
    path('color-create/', ColorCreateView.as_view(), name='color_create_view'),
    path('color-delete/<int:pk>/', color_delete_view, name='delete_color_view'),

    path('characteristics/', CharacteristicsListView.as_view(), name='characteristics_list_view'),
    path('characteristics/detail/<int:pk>/', characteristics_detail_view, name='char_edit_view'),
    path('characteristics/create/', CharacterCreateView.as_view(), name='char_create_view'),
    path('characteristics/delete/<int:pk>/', characteristic_delete_view, name='char_delete_view'),
    path('characteristics/value/edit/<int:pk>/', CharValueEditView.as_view(), name='char_value_edit_view'),
    path('characteristics/value/delete/<int:pk>/', delete_char_value_view, name='char_value_delete_view'),

    path('attributes-class/list/', AttributeClassListView.as_view(), name='attribute_class_list_view'),
    path('attributes-class/create/', AttributeClassCreateView.as_view(), name='attribute_class_create_view'),
    path('attributes-class/delete//<int:pk>/', attribute_class_delete_view, name='attribute_class_delete_view'),
    path('attributes-class/edit/<int:pk>/', attribute_class_edit_view, name='attribute_class_edit_view'),
    path('attribute-class-manager/<int:pk>/', attribute_class_manager_view, name='attribute_class_manager'),

    path('attributes-title/edit/<int:pk>/', AttributeTitleEditView.as_view(), name='attribute_title_edit_view'),
    path('attributes-title/delete/<int:pk>/', attribute_title_delete_view, name='attribute_title_delete_view'),

    path('warehouse-category/list/', WarehouseCategoryListView.as_view(), name='ware_cate_list_view'),
    path('warehouse-category/create/', WarehouseCategoryCreateView.as_view(), name='ware_cate_create_view'),
    path('warehouse-category/delete//<int:pk>/', warehouse_category_delete, name='ware_cate_delete_view'),
    path('warehouse-category/edit/<int:pk>/', WarehouseCategoryUpdateView.as_view(), name='ware_cate_edit_view'),

    path('gift-list/', GiftListView.as_view(), name='gift_list'),
    path('gift-edit/<int:pk>/', GiftUpdateView.as_view(), name='gift_edit_view'),
    path('gift-create/', GiftCreateView.as_view(), name='gift_create_view'),
    path('gift-delete/<int:pk>/', delete_gift_view, name='gift_delete_view'),
    path('gift-actions/<int:pk>/<int:dk>/', add_gift_action_view, name='add_gift_view'),


    path('attribute-related/list/', AttributeRelatedListView.as_view(), name='attr_related_list'),
    path('attribute-related/create/', AttributeRelatedCreateView.as_view(), name='attr_related_create'),
    path('attribute-related/update/<int:pk>/', AttributeRelatedUpdateView.as_view(), name='attr_related_update'),
    path('attribute-related/delete/<int:pk>/', attribute_related_delete_view, name='attr_related_delete'),

    #  handle qty views
    path('handle-qty-queryset/', QuickChangeProductWithQtyView.as_view(), name='handle_product_qty'),
    path('reset-qty-products/', reset_qty_to_products_view, name='reset_qty_products'),
    path('ajax/change-product-qty/<int:pk>/', ajax_quick_change_qty_to_product, name='ajax_change_product_qty'),

    path('change-site-status-view/', change_site_setting_status_view, name='change_site_status_view')

    ]
