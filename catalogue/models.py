from django.db import models
from django.db.models import Sum, Q, F
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils.text import slugify

import os, datetime
from decimal import Decimal
from tinymce.models import HTMLField

from site_settings.abstract_models import DefaultBasicModel
from .categories import Category, WarehouseCategory
from .product_details import Vendor, Brand, Color

from site_settings.constants import MEDIA_URL, CURRENCY, UNIT
from .managers import ProductManager
from .validators import upload_product_photo, validate_file

WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS
RETAIL_TRANSCATIONS = settings.RETAIL_TRANSCATIONS


class ProductClass(models.Model):
    title = models.CharField(unique=True, max_length=150)
    is_service = models.BooleanField(default=False, verbose_name='Υπηρεσία')
    have_transcations = models.BooleanField(default=True, verbose_name='Υποστηρίζει συναλλαγές')
    have_attribute = models.BooleanField(default=False, verbose_name='Μεγεθολόγιο')

    class Meta:
        verbose_name = 'Product Class'
        verbose_name_plural = 'Product Classes'

    def __str__(self):
        return self.title


class Product(DefaultBasicModel):
    warehouse_active = models.BooleanField(default=True, verbose_name='Ενεργό στην Αποθήκη')
    is_offer = models.BooleanField(default=False, verbose_name='Προσφορά')
    product_class = models.ForeignKey(ProductClass, on_delete=models.CASCADE, verbose_name='Είδος')
    featured_product = models.BooleanField(default=False, verbose_name='Εμφάνιση Πρώτη Σελίδα')

    #  warehouse data
    order_code = models.CharField(null=True, blank=True, max_length=100, verbose_name="Κωδικός Τιμολογίου")
    price_buy = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name="Αξία Αγοράς")
    order_discount = models.IntegerField(default=0, verbose_name="'Έκπτωση Τιμολογίου")
    category = models.ForeignKey(WarehouseCategory, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Κατηγορία Αποθήκης')
    vendor = models.ForeignKey(Vendor, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='Προμηθευτής')

    qty_measure = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name='Ποσότητα Ανά Τεμάχιο', blank=True, null=True)
    qty = models.IntegerField(default=0, verbose_name='Ποσότητα')
    qty_add = models.IntegerField(default=0.00, verbose_name="Υπόλοιπο", help_text='we use this for manual add.')
    qty_remove = models.IntegerField(default=0.00, verbose_name="Qty Remove", help_text='System use it only if warehouse transations')
    barcode = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True, verbose_name='Περιγραφή')
    measure_unit = models.CharField(max_length=1, default='1', choices=UNIT, blank=True, null=True, verbose_name='Μονάδα Μέτρησης')
    safe_stock = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Όριο αποθέματος')

    objects = models.Manager()
    my_query = ProductManager()

    #  site
    sku = models.CharField(max_length=150, blank=True, null=True)
    site_text = HTMLField(blank=True, null=True)
    category_site = models.ManyToManyField(Category, blank=True, null=True, verbose_name='Κατηγορία Site')
    brand = models.ForeignKey(Brand, blank=True, null=True, verbose_name='Brand', on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Χρωμα')
    slug = models.SlugField(blank=True, null=True, allow_unicode=True, max_length=240, db_index=True)

    # price sell and discount sells
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, verbose_name="Αρχική Τιμή")
    price_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Εκπτωτική Τιμή')
    final_price = models.DecimalField(default=0, decimal_places=2, max_digits=10, blank=True, verbose_name='Τιμή Πώλησης')

    related_products = models.ManyToManyField('self', blank=True, verbose_name='Related Products')
    different_color_products = models.ManyToManyField('self', blank='True', related_name='similar_color')

    class Meta:
        verbose_name_plural = "1. Products"
        ordering = ['-active', '-id', ]

    def save(self, *args, **kwargs):
        self.final_price = self.price_discount if self.price_discount > 0 else self.price
        self.is_offer = True if self.price_discount > 0 else False
        '''
        if self.product_class.have_transcations:
            if self.have_attr:
                self.qty = self.calculate_qty_if_attributes()
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            self.qty = self.qty_add - self.qty_remove
        '''
        super(Product, self).save(*args, **kwargs)

    def calculate_qty_if_attributes(self):
        attributes = self.attr_class.all().filter(class_related__have_transcations=True)
        attribute = attributes.first() if attributes.exists() else None
        if attribute is None:
            return 0
        if not WAREHOUSE_ORDERS_TRANSCATIONS and not RETAIL_TRANSCATIONS:
            qs = attribute.my_attributes.all()
            qty = qs.aggregate(Sum('qty'))['qty__sum'] if qs.exists() else 0
            return qty
        return 0

    def warehouse_calculations(self):
        if WAREHOUSE_ORDERS_TRANSCATIONS:
            warehouse_order_items = self.invoice_products.all()
            # we will calculate two different values, the incomes and outcomes
            warehouse_in_items = warehouse_order_items.filter(order__order_type__in=['1', '2', '4'])
            warehouse_out_items = warehouse_order_items.filter(order__order_type='5')
            warehouse_in_qty = warehouse_in_items.aggregate(Sum('qty'))['qty__sum'] if warehouse_in_items else 0
            warehouse_out_qty = warehouse_out_items.aggregate(Sum('qty'))['qty__sum'] if warehouse_out_items else 0
            self.qty_add = warehouse_in_qty - warehouse_out_qty
            self.save()

    def order_calculations(self):
        if not RETAIL_TRANSCATIONS:
            self.qty_remove = 0
            self.save()
            return ''
        if self.product_class.is_service:
            pass
        if not self.product_class.have_transcations:
            return self.qty
        order_items = self.retail_items.all()
        qty_analysis = order_items.values('order__order_type').annotate(total_qty=(Sum('qty'))).order_by(
            'order__order_type')
        for qty_data in qty_analysis:
            qty_remove = qty_data['total_qty'] if qty_data['order__order_type'] in ['r', 'e', 'wa'] else 0
            qty = qty_remove - qty_data['total_qty'] if qty_data['order__order_type'] in ['b', 'wr'] else qty_remove
        self.qty_remove = 0
        self.save()

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:product_detail', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('dashboard:product_delete',  kwargs={'pk': self.id})

    @property
    def have_attr(self):
        return self.product_class.have_attribute if self.product_class else False

    @property
    def support_transcations(self):
        product_class = self.product_class
        if product_class.is_service or not product_class.have_transcations:
            return False
        return True

    def get_copy_url(self):
        return reverse('dashboard:create_copy_product', kwargs={'pk': self.id})

    def get_cart_url(self):
        return reverse('cart:check', kwargs={'pk': self.id, 'action': 'add'})

    def get_absolute_url(self):
        return reverse('product_view', kwargs={'slug': self.slug})

    def tag_qty(self):
        return f'{self.qty}  {self.get_measure_unit_display()}'

    def check_if_new(self):
        diffence = datetime.datetime.now() - self.timestamp.replace(tzinfo=None)
        days = diffence.days
        if days < 61:
            return True
        return False

    @property
    def image(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_primary=True).last().image
        except:
            pass

    @property
    def secondary_image(self):
        try:
            return ProductPhotos.objects.filter(active=True, product=self, is_back=True).last().image
        except:
            pass

    def tag_final_price(self):
        return f'{self.final_price} {CURRENCY}'

    def tag_price(self):
        return f'{self.price} {CURRENCY}'

    def tag_price_discount(self):
        return f'{self.price_discount} {CURRENCY}'

    def tag_price_buy(self):
        return f'{self.price_buy} {CURRENCY}'

    def tag_discount_percent(self):
        if self.price_discount > 0 and self.price != 0:
            discount = round(100-(self.price_discount/self.price)*100, 0)
            return f'{discount}%'
        return '- 0%'

    def get_all_images(self):
        return ProductPhotos.objects.filter(active=True, product=self)

    def get_extra_images(self):
        return self.images.all().exclude(is_primary=True)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s%s" class="img-responsive">' % (MEDIA_URL, self.image))
        return mark_safe('<img src="%s" class="img-responsive">' % "{% static 'home/no_image.png' %}")

    def image_tag_tiny(self):
        if self.image:
            return mark_safe('<img src="%s%s" width="100px" height="100px">' % (MEDIA_URL, self.image))

    def show_warehouse_remain(self):
        return self.qty * self.measure_unit

    def tag_chart_size(self):
        chart_sizes = self.chartsize_set.all()
        if chart_sizes.exists():
            return chart_sizes.first()
        if self.brand:
            brand = self.brand
            chart_brand = brand.chartsize
            return chart_brand
        return None

    @staticmethod
    def filters_data(request, queryset):
        offer_name = request.GET.get('offer_name', None)
        search_name = request.GET.get('search_name', None)
        cate_name = request.GET.getlist('cate_name', None)
        cat = request.GET.get('cat', None)  # site category for fast search
        category_name = request.GET.getlist('category_name', None)   # used on frontend for categories site
        brand_name = request.GET.getlist('brand_name', None)
        active_name = request.GET.get('active_name', None)
        discount_name = request.GET.get('discount_name')
        qty_name = request.GET.get('qty_exists_name')
        vendor_name = request.GET.getlist('vendor_name', None)
        ware_cate = request.GET.getlist('ware_cate', None)
        attr_name = request.GET.getlist('attr_name', None)
        price_name = request.GET.get('price_name', None)
        price_name = price_name.split(';') if price_name else None
        color_name = request.GET.getlist('color_name', None)
        feature_name = request.GET.get('feature_name', None)
        char_name = request.GET.get('char_name', None)

        queryset = queryset.filter(is_offer=True) if offer_name == '1' else queryset
        queryset = queryset.filter(color__title__in=color_name) if color_name else queryset
        try:
            queryset = queryset.filter(final_price__range=price_name) if price_name else queryset
        except:
            queryset = queryset
        queryset = queryset.filter(category_site__slug__in=cate_name) if cate_name else queryset
        queryset = queryset.filter(category_site__id__in=category_name) if category_name else queryset
        queryset = queryset.filter(category_site__slug=cat) if cat else queryset
        queryset = queryset.filter(vendor__id__in=vendor_name) if vendor_name else queryset
        queryset = queryset.filter(category__id__in=ware_cate) if ware_cate else queryset
        queryset = queryset.filter(active=True) if active_name == '1' else queryset.filter(
            active=False) if active_name == '2' else queryset
        queryset = queryset.filter(featured_product=True) if feature_name == '1' else queryset
        queryset = queryset.filter(price_discount__gt=0) if discount_name else queryset
        queryset = queryset.filter(qty__gt=0) if qty_name else queryset

        queryset = queryset.filter(brand__slug__in=brand_name) if brand_name else queryset
        queryset = queryset.filter(Q(title__icontains=search_name.capitalize()) |
                                   Q(sku__contains=search_name) |
                                   Q(brand__title__contains=search_name)
                                   ).distinct() if search_name else queryset
        if attr_name:
            queryset = queryset.filter(product_class__have_attribute=True)

        order_by = request.GET.get('order_by', None)
        queryset = queryset.order_by(order_by) if order_by in ['title', '-title', 'final_price', '-final_price'] else queryset
        return queryset

    #   django table
    def delivery(self):
        if self.qty > 0:
            return 'positive'
        return 'warning'

    def color_qty(self):
        if self.qty > 0:
            return 'primary'
        return 'danger'


@receiver(post_save, sender=Product)
def create_slug(sender, instance, **kwargs):
    if not instance.slug:
        new_slug = slugify(instance.title, allow_unicode=True)
        qs_exists = Product.objects.filter(slug=new_slug).exists()
        instance.slug = f'{new_slug}-{instance.id}' if qs_exists else new_slug
        instance.save()


class ProductPhotos(models.Model):
    image = models.ImageField(upload_to=upload_product_photo, validators=[validate_file, ])
    alt = models.CharField(null=True, blank=True, max_length=200,
                           help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    title = models.CharField(null=True, blank=True, max_length=100,
                             help_text='Θα δημιουργηθεί αυτόματα εάν δεν συμπληρωθεί')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False, verbose_name='Primary Picture')
    is_back = models.BooleanField(default=False, verbose_name='Δεύτερη Εικόνα')

    class Meta:
        verbose_name_plural = 'Gallery'
        ordering = ['-is_primary', ]

    def save(self, *args, **kwargs):
        self.title = f'{self.product.title}' if self.product and not self.title else self.title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product.title

    def image_status(self):
        return 'Primary Image' if self.is_primary else 'Secondary Image' if self.is_back else 'Image'

    def tag_image(self):
        return mark_safe('<img width="150px" height="150px" src="%s%s" />' % (MEDIA_URL, self.image))

    tag_image.short_description = 'Photo'

    def tag_image_tiny(self):
        return mark_safe(f'<img width="150px" height="150px" src="{self.image.url}" />')

    tag_image_tiny.short_description = 'Εικόνα'

    def tag_status(self):
        return 'First Picture' if self.is_primary else 'Back Picture' if self.is_back else 'Picture'

    def tag_primary(self):
        return 'Αρχική Εικόνα' if self.is_primary else 'Εικόνα'

    def tag_secondary(self):
        return 'Δευτερευουσα εικόνα' if self.is_back else "Εικόνα"


class Gifts(models.Model):
    title = models.CharField(max_length=150, unique=True, verbose_name='Τιτλος')
    gift_message = models.CharField(max_length=200, unique=True, verbose_name='Μυνημα στον πελατη')
    status = models.BooleanField(default=False, verbose_name='Κατασταση')
    product_related = models.ManyToManyField(Product, related_name='product_related')
    products_gift = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, verbose_name='Δωρο')

    def __str__(self):
        return self.title

    def get_edit_url(self):
        return reverse('dashboard:gift_edit_view', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('dashboard:gift_delete_view', kwargs={'pk': self.id})

    def tag_status(self):
        return 'Active' if self.status else 'Non Active'





