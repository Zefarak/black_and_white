from .autocomplete_widgets import VendorAutocomplete, WarehouseCategoryAutocomplete, BrandAutocomplete
from django.urls import path
from .views import VendorListView, VendorCreateView, VendorUpdateView, delete_vendor
from .autocomplete_widgets import BrandAutocomplete, VendorAutocomplete, WarehouseCategoryAutocomplete

app_name = 'catalogue'

urlpatterns = [
    path('auto/vendors/', VendorAutocomplete.as_view(), name='vendors_auto'),
    path('auto/warehouse/', WarehouseCategoryAutocomplete.as_view(), name='warehouse_category_auto'),
    path('auto/brands/', BrandAutocomplete.as_view(), name='brand-autocomplete'),

    path('vendors/', VendorListView.as_view(), name='vendors'),
    path('vendor/<int:pk>/', VendorUpdateView.as_view(), name='vendor_detail'),
    path('vendors/create/', VendorCreateView.as_view(), name='vendor_create'),
    path('vendor/delete/<int:pk>/', delete_vendor, name='vendor_delete'),



]