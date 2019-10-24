from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .models import Voucher, VoucherRules, ProductRange


@receiver(post_save, sender=Voucher)
def create_voucher_subclasses(sender, instance, **kwargs):
    voucher_rules, created = VoucherRules.objects.get_or_create(voucher=instance)
    product_range = ProductRange.objects.get_or_create(voucher=instance)