from django.test import TestCase
from django.test.client import Client
from django.shortcuts import reverse
# Create your tests here.
from catalogue.models import Product, ProductClass, Gifts
from accounts.models import User

from cart.models import Cart, CartItem, CartSubscribe
from subscribe.models import Subscribe, UserSubscribe
from site_settings.models import Shipping, PaymentMethod
from point_of_sale.models import Order, OrderSubscribeDiscount, OrderItem, OrderGift, OrderSubscribe


class TestCartAndOrder(TestCase):

    def setUp(self):
        product_class = ProductClass.objects.create(title='Test')
        self.product_1 = Product.objects.create(title='Product_1', product_class=product_class, price=2)
        self.product_2 = Product.objects.create(title='Product_2', product_class=product_class, price=1)
        self.product_3 = Product.objects.create(title='Gift', product_class=product_class, price=0.5)
        self.user = User.objects.create(username='user')
        self.cart = Cart.objects.create(cart_id='dfdfdfsdfe', user=self.user)

        self.shipping_method = Shipping.objects.create(title='Shipping_title')
        self.payment_method = PaymentMethod.objects.create(title='Payment_title')

        self.subscribe = Subscribe.objects.create(title='Test_1', value=6, counter=3, category='a')
        self.subscribe.products.add(self.product_1)
        self.subscribe.save()
        self.cart_subscribe = CartSubscribe.objects.create(cart_related=self.cart, subscribe=self.subscribe)
        cart_item_1 = CartItem.add_product_to_cart(request='', cart=self.cart, product=self.product_1)
        cart_item_2 = CartItem.add_product_to_cart(request='', cart=self.cart, product=self.product_2)
        cart_item_3 = CartItem.add_product_to_cart(request='', cart=self.cart, product=self.product_1)

    def test_add_product_to_cart(self):
        cart = self.cart
        cart.refresh_from_db()

    def test_gifts(self):
        gift = Gifts.objects.create(
            products_gift=self.product_3,
            title='Test_1',

        )
        gift.product_related.add(self.product_1)
        gift.save()


    def xccxtest_order_creation(self):
        self.cart.refresh_from_db()
        new_order = Order.objects.create(
            user=self.user,
            payment_method=self.payment_method,
            order_type='e',
            shipping_method=self.shipping_method,
        )
        # new_order.create_subs_from_eshop_order(self.cart, self.user)
        # new_order.create_sub_discounts_from_eshop_order(self.cart, self.user)
        new_order.create_gifts(self.cart)
        print(new_order.gifts.count())


