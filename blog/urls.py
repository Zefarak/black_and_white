from django.urls import path


from .views import (BlogHomepageView, CategoryDetailView,
                    BlogDetailView,BlogCategoryListView,


                    )
from .ajax_views import ajax_delete_photo, ajax_add_images
app_name = 'blog'

urlpatterns = [
    path('', BlogHomepageView.as_view(), name='homepage'),
    path('κατηγορια/<str:slug>/', CategoryDetailView.as_view(), name='category_detail_view'),

    path('post/<slug:slug>/', BlogDetailView.as_view(), name='detail'),

    path('ajax/delete-photo/<int:pk>/', ajax_delete_photo, name='ajax_delete_photo'),
    path('ajax/add-images/<int:pk>/', ajax_add_images, name='ajax_add_images'),




]