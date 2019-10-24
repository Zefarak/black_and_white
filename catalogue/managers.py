from django.db import models
from site_settings.constants import RETAIL_TRANSCATIONS
from django.conf import settings
from datetime import datetime, timedelta
USE_QTY_LIMIT = settings.USE_QTY_LIMIT

one_month_earlier = datetime.now()


class ProductSiteQuerySet(models.query.QuerySet):

    def active_warehouse(self):
        if RETAIL_TRANSCATIONS:
            return self.filter(active=True)
        return self.filter(active=True)

    def active(self):
        return self.filter(active=True)

    def active_for_site(self):
        return self.filter(active=True, site_active=True, qty__gt=0) if USE_QTY_LIMIT else self.filter(active=True, site_active=True)

    def featured(self):
        return self.active_for_site().filter(is_featured=True)[:12]

    def category_queryset(self, cate):
        return self.active().filter(category_site__in=cate)


class ProductManager(models.Manager):

    def active(self):
        return super(ProductManager, self).filter(active=True)

    def featured_products(self):
        return self.active().filter(featured_product=True)

    def active_warehouse(self):
        return self.active()

    def products_with_offer(self):
        return self.active().filter(is_offer=True)

    def active_for_site(self):
        return self.active()

    def active_with_qty(self):
        return self.active_for_site().filter(qty__gte=0)

    def get_site_queryset(self):
        return ProductSiteQuerySet(self.model, using=self._db)

    def active_warehouse_with_attr(self):
        return self.active_warehouse().filter(size=True)

    def new_products(self):
        return self.active_for_site().filter(timestamp_gte=one_month_earlier)


class CategoryManager(models.Manager):
    def parent_categories(self):
        return super(CategoryManager, self).filter(active=True, parent__isnull=True)

    def navbar(self):
        return super(CategoryManager, self).filter(active=True, show_on_menu=True)


class AttributeManager(models.Manager):

    def active_for_site(self):
        return super(AttributeManager, self).filter(qty__gt=0)

    def product_attributes(self, product):
        return super(AttributeManager, self).filter(class_related__product_related=product)

    def product_attributes_with_qty(self, product):
        return self.product_attributes(product).filter(qty__gt=0)

    def instance_queryset(self, instance):
        return self.active_for_site().filter(product_related=instance)


class CharacteristicManager(models.Manager):

    def active(self):
        return super(CharacteristicManager, self).filter(active=True)

    def filter_access(self):
        return self.active().filter(is_filter=True)