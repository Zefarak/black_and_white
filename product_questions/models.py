from django.db import models

from catalogue.models import Product


class Question(models.Model):
    timestap = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    product_related = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField()
    is_readed = models.BooleanField(default=False)

    def __str__(self):
        return f'Ερώτηση {self.id}'