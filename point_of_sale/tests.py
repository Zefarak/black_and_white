from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test import Client
from .models import Product, Order, OrderItem, Profile, OrderGift

from cart.models import Cart, CartItem, CartItemGifts, CartSubscribe
from catalogue.models import ProductClass, Gifts

from subscribe.models import Subscribe, UserSubscribe

'''
class TestOrderCreation(TestCase):

    def setUp(self):
        product_class = ProductClass.objects.create(title='No Chart', have_attribute=False)
        self.product = Product.objects.create(price=5, qty=10, title='Product A', product_class=product_class)
        self.profile = Profile.objects.create(first_name='Chris', last_name='Sta')

    def test_warehouse_movements(self):
        initial_qty = self.product.qty
        order = Order.objects.create(title='Order 666', order_type='r', profile=self.profile)
        self.order_item = OrderItem.objects.create(order=order,
                                                   title=self.product,
                                                   value=self.product.final_price,
                                                   qty=4
                                                   )
        expected_qty = initial_qty - 4
        self.assertEqual(expected_qty, self.product.qty)
        self.assertEqual(self.profile.balance, order.final_value)
        order_2 = Order.objects.create(title='Order 66r', order_type='b', profile=self.profile)
        self.order_item = OrderItem.objects.create(order=order_2,
                                                   title=self.product,
                                                   value=self.product.final_price,
                                                   qty=4
                                                   )
        expected_qty = initial_qty
        self.assertEqual(expected_qty, self.product.qty)
        self.assertEqual(self.profile.balance, 0)
'''


class TestEshopOrder(TestCase):

    def setUp(self):
        self.c = Client()
        self.my_user = User.objects.create(username='Testuser')
        product_class = ProductClass.objects.create(title='No Chart', have_attribute=False)
        self.product = Product.objects.create(price=5, qty=10, title='Product A', product_class=product_class)
        self.product_2 = Product.objects.create(price=2, qty=10, title='Product B', product_class=product_class)
        self.product_3 = Product.objects.create(price=5, qty=10, title='Product C', product_class=product_class)

        self.gift = Gifts.objects.create(title='Test Gift',
                                         products_gift=self.product_3,
                                         status=True,
                                         gift_message='lol'
                                         )
        self.gift.product_related.add(self.product)
        self.gift.save()

        self.profile = Profile.objects.create(first_name='Chris', last_name='Sta')

        self.subscription = Subscribe.objects.create(title='Test Sub', value=4, counter=3)
        self.subscription.products.add(self.product_2)
        self.subscription.save()

        new_cart = Cart.objects.create(cart_id='dsdsdeeeefeffsdfldspf[sdf', user=self.my_user)
        cart_exists, message = CartItem.create_cart_item(new_cart, self.product, 1)
        CartItemGifts.check_if_gift_exists(CartItem.objects.first())
        cart_item = CartItem.objects.first()
        new_sub = CartSubscribe.check_if_user_can_add_subscription(new_cart, self.subscription, self.my_user)
        self.cart = new_cart

    def test_cart_creation(self):
        new_cart = Cart.objects.create(cart_id='dsdsdeeeefeffsdfldspf[sdf', user=self.my_user)
        cart_exists, message = CartItem.create_cart_item(new_cart, self.product, 1)
        CartItemGifts.check_if_gift_exists(CartItem.objects.first())
        cart_item = CartItem.objects.first()
        self.cart = new_cart
        self.assertEqual(new_cart.user, self.my_user)
        self.assertEqual(cart_item.final_value, new_cart.final_value)
        self.assertEqual(CartItemGifts.objects.first().product, self.product_3)

    def test_subscription(self):
        new_cart = Cart.objects.create(cart_id='dsdsdeeeefeffsdfldspf[sdf', user=self.my_user)
        new_sub = CartSubscribe.check_if_user_can_add_subscription(new_cart, self.subscription, self.my_user)

        self.assertEqual(new_cart.final_value, new_sub.value)

    def test_create_order(self):
        request = self.c.get('/')
        request.user = self.my_user
        new_order = Order.objects.create(
            title='test',
            order_type='e',
            cart_related=self.cart,
            user=self.my_user,
        )
        for item in self.cart.order_items.all():
            OrderItem.create_or_edit_item(new_order, item.product, item.qty, 'ADD')
        for item in self.cart.gifts:
            OrderGift.objects.create(order=new_order, product=item.product, cart_gift=item, qty=item.qty)
        sub, sub_qs = UserSubscribe.check_active_subscription(self.my_user)
        if not sub:
            if self.cart.cartsubscribe:
                current_sub = UserSubscribe.create_subscription(self.cart.cartsubscribe.subscribe, self.my_user)
            else:
                current_sub = None
        else:
            current_sub = sub_qs.first()
        if current_sub:
            uses, value = 0, 0
            for order_item in new_order.order_items.all():
                if order_item.product in current_sub.subscribe.products.all():
                    uses += order_item.qty
                    value += order_item.total_value
        pass
        self.assertEqual(self.cart.final_value, 9)

        
