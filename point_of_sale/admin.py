from django.contrib import admin

from .models import OrderItemAttribute, OrderItem, Order, OrderProfile


@admin.register(OrderItemAttribute)
class OrderItemAttrAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class Order(admin.ModelAdmin):
    pass


@admin.register(OrderProfile)
class ProfileAdmin(admin.ModelAdmin):
    pass
