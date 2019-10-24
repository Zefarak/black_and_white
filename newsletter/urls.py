from django.urls import path

from .views import NewsLetterListView, NewsLetterUpdateView, delete_newsletter_view, NewsLetterCreateView, download_newsletter_view, validate_frontend_newsletter_view

app_name = 'newsletter'

urlpatterns = [
    path('list/', NewsLetterListView.as_view(), name='list'),
    path('update/<int:pk>/', NewsLetterUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', delete_newsletter_view, name='delete'),
    path('create/', NewsLetterCreateView.as_view(), name='create'),
    path('download/', download_newsletter_view, name='download_newsletter'),
    path('frontend/validate/email/', validate_frontend_newsletter_view, name='validate_newsletter')

]
