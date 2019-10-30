from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import CartItem


@receiver(post_save, sender=CartItem)
def check_gifts_on_creation(sender, instance, created, **kwargs):
    if created:
        pass
