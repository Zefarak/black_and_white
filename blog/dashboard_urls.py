from django.urls import path

from .dashboard_views import (BlogListView, CreatePostView, PostUpdateView, delete_post_view, PostCategoryListView,
                    PostCategoryUpdateView, PostCategoryCreateView, post_category_delete_view, BlogHomepageView,
                    delete_url_view, create_new_url_view,
                    )

app_name = 'dashboard_blog'

urlpatterns = [
    path('', BlogHomepageView.as_view(), name='homepage'),
    path('list/', BlogListView.as_view(), name='list_view'),
    path('create/', CreatePostView.as_view(), name='create_view'),
    path('post/update/<int:pk>/', PostUpdateView.as_view(), name='update_view'),
    path('delete/<int:pk>/', delete_post_view, name='delete_view'),

    path('post-category/', PostCategoryListView.as_view(), name='post_category_list'),
    path('post-category/create/', PostCategoryCreateView.as_view(), name='post_category_create'),
    path('post-category/update/<int:pk>/', PostCategoryUpdateView.as_view(), name='post_category_update'),
    path('post-category/delete/<int:pk>/', post_category_delete_view, name='post_category_delete'),
    path('post-url/create/<int:pk>/', create_new_url_view, name='create_url'),
    path('post-url/delete/<int:pk>/', delete_url_view, name='delete_url'),

]