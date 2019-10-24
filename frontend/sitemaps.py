from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from catalogue.models import Brand, Category


class BrandSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Brand.objects.filter(active=True)


class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return Category.objects.filter(active=True)


class StaticViewsSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'


    def items(self):
        return ['homepage', 'offer_view', 'search_page', 'new_products_view', 'contact_view',
                'brands_view', 'register_view', 'personal_data_view', 'contact_view',
                'return_policy_view', 'terms_rules_view', 'shipping_list_view', 'payment_list_view'

                ]

    def location(self, obj):
        return reverse(obj)
