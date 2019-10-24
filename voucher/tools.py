

def calculate_product_benefit_helper(self, instance, offer_type, value, discount_type):
    discount_value = 0
    items = instance.order_items.all()

    if offer_type == 'Site':
        for item in items:
            discount_value += item.final_value * (value / 100) if discount_type == 'Percentage' else \
            instance.order_items.count() * value if discount_type == 'Absolute' else value \
                if discount_type == 'Fixed Price' else 0
        discount_value = instance.final_value * (value / 100) if discount_type == 'Percentage' else \
            instance.order_items.count() * value if discount_type == 'Absolute' else value \
                if discount_type == 'Fixed Price' else 0
        if discount_type == 'Multibuy':
            order_item = instance.order_items.all().order_by('final_value').first()
            discount_value = order_item.final_value

    if offer_type == 'Category':
        for order_item in items:
            for category in order_item.product.category_site.all():
                if category in self.included_categories.all():
                    if discount_type == 'Percentage':
                        discount_value += order_item.total_value * (value / 100)
                    if discount_type == 'Absolute':
                        discount_value += value
                    if discount_value == "Fixed Price":
                        discount_value = value
                        break
                    if discount_value == 'Multibuy':
                        pass

    if offer_type == 'Brand':
        for order_item in items:
            if order_item.product.brand in self.included_brands.all():
                if discount_type == 'Percentage':
                    discount_value += order_item.total_value * (value / 100)
                if discount_type == 'Absolute':
                    discount_value += value
                if discount_value == "Fixed Price":
                    discount_value = value
                    break
                if discount_value == 'Multibuy':
                    pass

    if offer_type == 'Products':
        order_items = instance.order_items.all()
        for order_item in order_items:
            if order_item.product in self.included_products:
                if discount_type == 'Percentage':
                    discount_value += order_item.final_value * (value / 100)
                if discount_type == 'Absolute':
                    discount_value += value
                if discount_value == "Fixed Price":
                    discount_value = value
                    break
                if discount_value == 'Multibuy':
                    pass
    return discount_value


