from django.db import models
from django.shortcuts import reverse
from catalogue.models import Product, Brand


def upload_photo(instance, filename):
    return f'chart_size/filename'


class ChartSize(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατασταση')
    title = models.CharField(unique=True, max_length=150, verbose_name='Ονομασια')
    image = models.ImageField(upload_to=upload_photo, )
    brand = models.OneToOneField(Brand, blank=True, on_delete=models.SET_NULL, null=True)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('size_chart:update', kwargs={'pk': self.id})

    def get_card_url(self):
        return reverse('size_chart:chart_manager', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('size_chart:delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        search_name = request.GET.get('search_name', None)
        active_name = request.GET.get('active_name', None)
        qs = qs.filter(title__icontains=search_name) if search_name else qs
        qs = qs.filter(active=True) if active_name else qs
        return qs
