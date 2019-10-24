from django.urls import path

from .views import ContactListView, ContactUpdateView, validate_frontend_contact_form_view
app_name = 'contact'

urlpatterns = [
    path('list/', ContactListView.as_view(), name='contact_list'),
    path('detail/<int:pk>/', ContactUpdateView.as_view(), name='contact_detail'),

    path('frontend/validate-contact-form/', validate_frontend_contact_form_view, name='validate_frontend_form'),

]