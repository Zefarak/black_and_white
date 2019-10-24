from django.test import TestCase

from .models import Product, Order, OrderItem, Profile
from catalogue.models import ProductClass


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

