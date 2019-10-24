from django.contrib import admin
from .models import Cart, CartItemAttribute, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass



@admin.register(CartItemAttribute)
class CartItemAttrAdmin(admin.ModelAdmin):
    pass


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'qty']