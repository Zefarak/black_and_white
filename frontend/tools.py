from catalogue.product_details import Brand, Color
from catalogue.categories import Category
from django.shortcuts import get_object_or_404


def category_filter_data(queryset):
    brands_id = queryset.values_list('brand', flat=False)
    brands = Brand.objects.filter(id__in=brands_id)
    categories_id = queryset.values_list('category_site', flat=False)
    categories = Category.objects.filter(id__in=categories_id)
    return [categories, brands]


def get_colors_from_queryset(queryset):
    colors_id = queryset.values_list('color', flat=True)
    colors = Color.objects.filter(active=True, id__in=colors_id)
    return colors


def category_and_brands_filter_data(queryset, cate_id=None):
    brands_id = queryset.values_list('brand', flat=False)
    brands = Brand.objects.filter(id__in=brands_id)
    category = get_object_or_404(Category, id=cate_id)
    categories = []
    for cate in category.get_childrens():
        categories.append(cate)
        for cate_ in cate.get_childrens():
            categories.append(cate_)
    return [categories, brands]
