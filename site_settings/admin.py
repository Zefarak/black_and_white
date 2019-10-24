from django.contrib import admin
from .models import Store, PaymentMethod, Company
# Register your models here.


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    pass


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    pass


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    pass
