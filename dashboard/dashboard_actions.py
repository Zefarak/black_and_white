from django.shortcuts import get_object_or_404, redirect, reverse
from django.contrib.admin.views.decorators import staff_member_required

from catalogue.models import Product, Gifts
from site_settings.models import SiteSettings
from catalogue.product_attritubes import Attribute, AttributeProductClass


@staff_member_required
def copy_product_view(request, pk):
    old_object = get_object_or_404(Product, id=pk)
    object = get_object_or_404(Product, id=pk)
    object.id = None
    object.qty = 0
    object.slug = None
    object.save()
    object.refresh_from_db()
    for ele in old_object.category_site.all():
        object.category_site.add(ele)
    for ele in old_object.characteristics.all():
        object.characteristics.add(ele)
    
    for attr_class in old_object.attr_class.all():
        all_attributes = attr_class.my_attributes.all()
        attr_class.id = None
        attr_class.product_related = object
        attr_class.save()
        attr_class.refresh_from_db()
        for title in all_attributes:
            title.id=None
            title.class_related = attr_class
            title.qty = 0
            title.save()
    return redirect(object.get_edit_url())


@staff_member_required
def add_gift_action_view(request, pk, dk):
    print('works!')
    gift = get_object_or_404(Gifts, id=pk)
    instance = get_object_or_404(Product, id=dk)
    gift.products_gift = instance
    gift.save()
    return redirect(gift.get_edit_url())


@staff_member_required
def reset_qty_to_products_view(request):
    qs = Product.objects.filter(product_class__have_transcations=True)
    qs.update(qty=0)
    return redirect(reverse('dashboard:handle_product_qty'))


@staff_member_required
def change_site_setting_status_view(request):
    instance = SiteSettings.objects.first()
    is_open = instance.is_open
    instance.is_open = False if is_open else True
    instance.save()
    return redirect(reverse('dashboard:home'))