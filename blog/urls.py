from django.urls import path

from .views import (BlogHomepageView, BlogDetailView,BlogCategoryListView,


                    )
from .ajax_views import ajax_delete_photo, ajax_add_images
app_name = 'blog'

urlpatterns = [
    path('', BlogCategoryListView.as_view(), name='blog_category'),
    path('κατηγορια/<slug/slug>/', BlogHomepageView.as_view(), name='category_detail'),

    path('post/<slug:slug>/', BlogDetailView.as_view(), name='detail'),

    path('ajax/delete-photo/<int:pk>/', ajax_delete_photo, name='ajax_delete_photo'),
    path('ajax/add-images/<int:pk>/', ajax_add_images, name='ajax_add_images'),




]