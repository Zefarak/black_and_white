from django.test import TestCase

from catalogue.models import Product, ProductClass, Brand, Category
from cart.models import CartItem, Cart
from .models import Voucher, VoucherRules
from decimal import Decimal
from site_settings.models import Shipping
from point_of_sale.models import Order, OrderItem

class CreateDatabaseTest(TestCase):

    def create_product_class(self, title):
        return ProductClass.objects.create(title=title)

    def create_brand(self, title):
        return Brand.objects.create(title=title)

    def create_category(self, name):
        return Category.objects.create(name=name)

    def create_product(self, title, product_class, brand, category, price, qty):
        product = Product.objects.create(title=title,
                                      product_class=product_class,
                                      brand=brand,
                                      price=price,
                                      qty=qty,
                                      )
        product.category_site.add(category)
        product.save()
        return product

    def create_cart(self, cart_id):
        return Cart.objects.create(cart_id=cart_id)

    def create_cart_item(self, cart, product, qty):
        return CartItem.objects.create(cart=cart, product=product, qty=qty)

    def create_shipping_method(self, title, limit_value, cost):
        return Shipping.objects.create(title=title, limit_value=limit_value, additional_cost=cost)

    def setUp(self):
        product_class = self.create_product_class('Product Class A')
        self.brand = self.create_brand('Brand A')
        self.category = self.create_category('Category A')
        self.product = self.create_product('Product A', product_class, self.brand, self.category, 25, 10)
        self.shipping = self.create_shipping_method('Geniki Metaforiki', 50, 5)
        self.cart = self.create_cart('fdfdfwfwfwefeccwcwewcwrerwr')
        self.cart.shipping_method = self.shipping
        self.cart.save()
        self.cart_item = self.create_cart_item(self.cart, self.product, 1)

    def test_free_shipping_voucher(self):
        voucher = Voucher.objects.create(name='Free Shipping')
        rule = voucher.voucher_rule
        rule.benefit_type = 'Shipping absolute'
        rule.save()
        self.assertEqual(Decimal('30.00'), self.cart.final_value)
        self.cart.vouchers.add(voucher)
        self.cart.save()
        self.assertEqual(Decimal('25.00'), self.cart.final_value)

    def _test_percent_voucher_and_site_settings(self):
        voucher = Voucher.objects.create(name='10% Discount', )
        rule = voucher.voucher_rule
        rule.value = 10
        rule.benefit_type = "Percentage"
        rule.save()
        rule.offer_type = "Site"
        rule.save()
        old_value = self.cart.final_value * (100 - rule.value) / 100
        self.cart.vouchers.add(voucher)
        self.cart.save()
        self.assertEqual(old_value, self.cart.final_value)
        self.cart.vouchers.remove(voucher)
        self.cart.save()

    def test_percent_voucher_and_category_settings(self):
        voucher = Voucher.objects.create(name='10% Discount', )
        rule = voucher.voucher_rule
        rule.value = 10
        rule.benefit_type = "Percentage"
        rule.save()
        rule.offer_type = "Category"
        rule.save()
        p_range = voucher.voucher_range
        p_range.included_categories.add(self.category)
        p_range.save()
        old_value = (self.cart.value * (100 - rule.value) / 100) + 5

        self.cart.vouchers.add(voucher)
        self.cart.save()
        self.assertEqual(old_value, self.cart.final_value)
        self.cart.vouchers.remove(voucher)
        self.cart.save()

    def test_percent_voucher_and_brand_settings(self):
        voucher = Voucher.objects.create(name='10% Discount', )
        rule = voucher.voucher_rule
        rule.value = 10
        rule.benefit_type = "Percentage"
        rule.save()
        rule.offer_type = "Brand"
        rule.save()
        p_range = voucher.voucher_range
        p_range.included_brands.add(self.brand)
        p_range.save()
        old_value = (self.cart.value * (100-rule.value)/100) + 5
        self.cart.vouchers.add(voucher)
        self.cart.save()
        self.assertEqual(old_value, self.cart.final_value)
        self.cart.vouchers.remove(voucher)
        self.cart.save()

    def test_fixed_and_site_settings(self):
        voucher = Voucher.objects.create(name='10% Discount', )
        rule = voucher.voucher_rule
        rule.value = 5
        rule.benefit_type = "Absolute"
        rule.save()
        rule.offer_type = "Site"
        rule.save()
        estimate_value = (self.cart.final_value - (self.cart.order_items.count()*5))
        self.cart.vouchers.add(voucher)
        self.cart.save()
        self.assertEqual(estimate_value, self.cart.final_value)
        self.cart.vouchers.remove(voucher)
        self.cart.save()

    def test_order(self):
        cart = self.cart
        order = Order.objects.create(title='Test',
                                     cart_related=cart,
                                     shipping_method=cart.shipping_method,
                                     value=cart.value,
                                     )
        voucher = Voucher.objects.create(name='Free Shipping')
        rule = voucher.voucher_rule
        rule.benefit_type = 'Shipping absolute'
        rule.save()
        order.vouchers.add(voucher)
        order.save()

    def test_order_with_register_voucher(self):
        cart = self.cart
        cart.active = True
        voucher = Voucher.objects.create(name='Free Shipping', usage='Once per customer', active=True)
        rule = voucher.voucher_rule
        rule.value = 10
        rule.save()
        order = Order.objects.create(title='Test',
                                     cart_related=cart,
                                     shipping_method=cart.shipping_method,
                                     value=cart.value,
                                     )
        for item in cart.order_items.all():
            new_item = OrderItem.objects.create(
                order=order,
                title=item.product,
                qty=item.qty,
            )
        estimate_value = order.final_value * Decimal(0.9)
        order.vouchers.add(voucher)
        order.save()
        self.assertEqual(round(estimate_value, 2), order.final_value)


