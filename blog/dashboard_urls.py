from django.urls import path

from .views import BlogListView, CreatePostView, PostUpdateView, delete_post_view

app_name = 'dashboard_blog'

urlpatterns = [
    path('', BlogListView.as_view(), name='list_view'),
    path('create/', CreatePostView.as_view(), name='create_view'),
    path('post/update/<int:pk>/', PostUpdateView.as_view(), name='update_view'),
    path('delete/<int:pk>/', delete_post_view, name='delete_view'),

]