from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
        path('password-reset/', auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html'), name='password_reset'),
        path('password-reset-done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
        path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete')
    ]
