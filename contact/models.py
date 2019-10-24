from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.conf import settings

SITE_EMAIL = settings.SITE_EMAIL

class Contact(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    is_readed = models.BooleanField(default=False)
    email = models.EmailField(verbose_name='Email *')
    name = models.CharField(max_length=200, verbose_name='Ονοματεπώνυμο *')
    phone_number = models.CharField(max_length=10, blank=True, verbose_name='Τηλέφωνο')
    message = models.TextField(verbose_name='Μήνυμα *')

    def __str__(self):
        return self.email

    def get_edit_url(self):
        return reverse('contact:contact_detail', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        is_readed_name = request.GET.get('is_readed_name', None)

        queryset = queryset.filter(is_readed=True) if is_readed_name == '1'\
            else queryset.filter(is_readed=False) if is_readed_name == '2' else queryset
        queryset = queryset.filter(Q(email__contains=search_name)|
                                   Q(phone_number__contains=search_name) |
                                   Q(name__contains=search_name)
                                   ).distinct() if search_name else queryset
        return queryset


@receiver(post_save, sender=Contact)
def send_info_to_site_user(sender, instance, created, **kwargs):
    if created:
        send_mail('Νέο Μηνυμα από πελάτη', f'{instance.email}', f'{instance.email}', [SITE_EMAIL])
