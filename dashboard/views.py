from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, View, DeleteView
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Q, Sum
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.conf import settings
from django.db import models
from django_tables2 import RequestConfig
from catalogue.models import Product, ProductPhotos, WarehouseCategory, Gifts
from catalogue.categories import Category
from catalogue.product_details import Brand, Vendor
from catalogue.forms import CreateProductForm, ProductPhotoUploadForm, ProductCharacteristicForm, WarehouseCategoryForm, GiftForm
from .product_forms import ProductForm, ProductFormWithQty
from .tables import TableProduct, WarehouseCategoryTable, ProductTable, ProductDiscountTable, GiftTable
from point_of_sale.tables import OrderTable
from catalogue.product_attritubes import ProductCharacteristics, Characteristics, CharacteristicsValue, Attribute, AttributeTitle, AttributeClass, AttributeProductClass
from .models import ProductDiscount
from .forms import ProductDiscountForm
from point_of_sale.models import Order, OrderItem
from contact.models import Contact
from newsletter.models import NewsLetter

from site_settings.models import SiteSettings

CURRENCY = settings.CURRENCY
WAREHOUSE_ORDERS_TRANSCATIONS = settings.WAREHOUSE_ORDERS_TRANSCATIONS


@method_decorator(staff_member_required, name='dispatch')
class DashBoard(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(DashBoard, self).get_context_data(**kwargs)
        new_orders = Order.my_query.get_queryset().new_orders()
        queryset_table = OrderTable(new_orders)
        new_messages = Contact.objects.filter(is_readed=False)
        newsletters = NewsLetter.objects.all().count()
        today_orders = Order.my_query.get_queryset().today_sells()
        today_orders = today_orders.aggregate(Sum('final_value'))['final_value__sum'] if today_orders else 0
        active_products = Product.objects.all().filter(active=True)[:10]

        currency = CURRENCY
        site_setting = SiteSettings.objects.first()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductsListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = Product
    paginate_by = 50
    total_products = 0

    def get_queryset(self):
        queryset = Product.filters_data(self.request, Product.objects.all())
        self.total_products = queryset.count() if queryset else 0
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductsListView, self).get_context_data(**kwargs)
        back_url, create_url = reverse('dashboard:home'), reverse('dashboard:product_create')
        page_title = 'Προϊόντα'
        queryset_table = TableProduct(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(queryset_table)
        # filters
        search_filter, vendor_filter, category_filter, active_filter, qty_filter, brand_filter, feature_filter = [True] * 7
        categories, vendors, brands = WarehouseCategory.objects.filter(
            active=True), Vendor.objects.all(), Brand.objects.all()
        #  reports
        reports, report_url = True, reverse('dashboard:ajax_product_analysis')
        context.update(locals())
        return context

    #  not use for now
    '''
    def post(self, *args, **kwargs):
        get_products = self.request.POST.getlist('choice_name', None)
        new_brand = get_object_or_404(Brand, id=self.request.POST.get('change_brand')) \
            if self.request.POST.get('change_brand') else None
        new_category = get_object_or_404(Category, id=self.request.POST.get('change_cate')) \
            if self.request.POST.get('change_cate') else None
        new_cate_site = get_object_or_404(Category, id=self.request.POST.get('change_cate_site')) \
            if self.request.POST.get('change_cate_site') else None
        new_vendor = get_object_or_404(Vendor, id=self.request.POST.get('change_vendor')) \
            if self.request.POST.get('change_vendor') else None
        if new_brand and get_products:
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                product.brand = new_brand
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_brand.title)
            return redirect('dashboard:products')
        if new_category and get_products:
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                product.category = new_category
                product.save()
            messages.success(self.request, 'The brand %s added on the products' % new_category.title)
            return redirect('dashboard:products')
        if new_cate_site and get_products:
            for product_id in get_products:
                product = get_object_or_404(Product, id=product_id)
                product.category_site.add(new_cate_site)
                product.save()
            messages.success(self.request, 'The category %s added in the products' % new_cate_site.title)

        if new_vendor:
            queryset = Product.objects.all()
            queryset = Product.filters_data(self.request, queryset)
            queryset.update(vendor=new_vendor)
            messages.success(self.request, 'The Vendor Updated!')
        return render(self.request, self.template_name)
    '''


@method_decorator(staff_member_required, name='dispatch')
class ProductCreateView(CreateView):
    template_name = 'dashboard/form.html'
    form_class = CreateProductForm
    new_object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία νέου Προϊόντος', self.request.GET.get('next', None)
        back_url = back_url if back_url else reverse('dashboard:products')
        context.update(locals())
        return context

    def form_valid(self, form):
        object = form.save()
        object.refresh_from_db()
        self.new_object = object
        return super().form_valid(form)

    def get_success_url(self):
        self.new_object.refresh_from_db()
        return reverse('dashboard:product_detail', kwargs={'pk': self.new_object.id})


@staff_member_required
def product_detail(request, pk):
    instance = get_object_or_404(Product, id=pk)
    have_transcations = instance.product_class.have_transcations
    print('product_class', instance.product_class.have_transcations)
    products, currency, page_title = True, CURRENCY, '%s' % instance.title
    images = instance.get_all_images()
    form = ProductFormWithQty(instance=instance) if have_transcations else ProductForm(instance=instance)
    if '_save' in request.POST:
        form = ProductFormWithQty(request.POST, instance=instance) if have_transcations else ProductForm(request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'The products %s is saves!')
            return HttpResponseRedirect(reverse('dashboard:products'))
        else:
            print('form_invalid', form.errors)

    if '_update' in request.POST:
        form = ProductFormWithQty(request.POST, instance=instance) if have_transcations else ProductForm(
            request.POST or None, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, f'Το Προϊόν {instance.title} τροποποιήθηκε.')
            return HttpResponseRedirect(reverse('dashboard:product_detail', kwargs={'pk': pk}))
        else:
            for error in form.errors:
                print(error)

    context = locals()
    return render(request, 'dashboard/product_detail.html', context)


@staff_member_required
def product_report_view(request, pk):
    instance = get_object_or_404(Product, id=pk)
    warehouse_movements = instance.invoice_products.all()
    retail_movements = instance.retail_items.all()
    back_url = instance.get_edit_url()

    #  filters
    date_filter = [True] * 1

    context = locals()
    return render(request, 'dashboard/product_report_page.html', context)


@staff_member_required
def copy_product_view(request, pk):
    product = get_object_or_404(Product, id=pk)
    new_product = Product.objects.get(id=pk)
    new_product.pk = None
    new_product.slug = ''
    new_product.save()
    new_product.refresh_from_db()
    return redirect(new_product.get_edit_url())


@staff_member_required
def delete_product(request, pk):
    instance = get_object_or_404(Product, id=pk)
    try:
        instance.delete()
        for image in instance.images.all():
            image.delete()
        for char in instance.characteristics.all():
            char.delete()
        for ele in instance.attr_class.all():
            ele.delete()
    except models.ProtectedError:
        messages.warning(request, 'You cant delete it because its already used.')
        return redirect(instance.get_edit_url())
    return HttpResponseRedirect(reverse('dashboard:products'))


@method_decorator(staff_member_required, name='dispatch')
class CategorySiteManagerView(ListView):
    template_name = 'dashboard/product_manager_view.html'
    model = Category

    def get_queryset(self):
        queryset = Category.objects.filter(active=True)
        queryset = Category.filter_data(queryset, self.request)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategorySiteManagerView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        page_title, back_url = 'Category Site Manager', instance.get_edit_url()
        selected_data = instance.category_site.all()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductMultipleImagesView(View):
    template_name = 'dashboard/photo_manager.html'

    def get(self, request, pk):
        instance = get_object_or_404(Product, id=pk)
        photos = ProductPhotos.objects.filter(product=instance)
        form = ProductPhotoUploadForm()
        return render(request, self.template_name, context=locals())

    def post(self, request, pk):
        data = {}
        instance = get_object_or_404(Product, id=pk)
        form = ProductPhotoUploadForm()
        if request.POST:
            form = ProductPhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                photo = ProductPhotos.objects.create(product=instance,
                                                     image=form.cleaned_data.get('image')
                                                     )
                data = {'is_valid': True,
                        'name': photo.product.title,
                        'url': photo.image.url
                        }
        instance.refresh_from_db()
        photos = instance.images.all()
        data['html_data'] = render_to_string(request=request,
                                             template_name='dashboard/ajax_calls/images.html',
                                             context={'photos': photos,
                                                      'instance': instance
                                                      }
                                             )
        return JsonResponse(data)


@method_decorator(staff_member_required, name='dispatch')
class CharacteristicsManagerView(ListView):
    model = Characteristics
    template_name = 'dashboard/product_manager_view.html'

    def get_queryset(self):
        queryset = Characteristics.objects.all()
        self.instance = get_object_or_404(Product, id=self.kwargs['pk'])
        queryset = queryset.exclude(productcharacteristics__product_related=self.instance)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        page_title, chars, back_url = 'Manager Χαρακτηριστικών', True, instance.get_edit_url()
        selected_data = instance.characteristics.all()
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductCharacteristicCreateView(CreateView):
    model = ProductCharacteristics
    template_name = 'dashboard/form.html'
    form_class = ProductCharacteristicForm

    def get_initial(self):
        initial = super().get_initial()
        self.instance = get_object_or_404(Product, id=self.kwargs['pk'])
        self.char = get_object_or_404(Characteristics, id=self.kwargs['dk'])
        initial['product_related'] = self.instance
        initial['title'] = self.char
        return initial

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['value'].queryset = CharacteristicsValue.objects.filter(char_related=self.char)
        return form

    def get_success_url(self):
        return reverse('dashboard:char_manager_view', kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'The Characteristic is created')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title = f'Create New Characteristic for {self.instance.title}'
        back_url, delete_url = self.get_success_url(), None,

        context.update(locals())
        return context


@staff_member_required
def product_characteristic_delete_view(request, pk):
    print('here!')
    instance = get_object_or_404(ProductCharacteristics, id=pk)
    instance.delete()
    return HttpResponseRedirect(reverse('dashboard:char_manager_view', kwargs={'pk': instance.product_related.id}))


@method_decorator(staff_member_required, name='dispatch')
class ProductCharacteristicEditView(UpdateView):
    model = ProductCharacteristics
    form_class = ProductCharacteristicForm


@method_decorator(staff_member_required, name='dispatch')
class ProductAttributeManagerView(ListView):
    template_name = 'dashboard/product_manager_view.html'
    model = AttributeClass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        page_title, attrs, back_url = f'Δημιουργία Μεγεθολογίων', True, instance.get_edit_url()
        selected_data = instance.my_attr_class.all()
        context.update(locals())
        return context


@staff_member_required
def create_attr_product_class(request, pk, dk):
    instance = get_object_or_404(Product, id=pk)
    attribute_class = get_object_or_404(AttributeClass, id=dk)
    attribute_class.products.add(instance)
    attribute_class.save()
    messages.success(request, 'Το μεγεθολογιο Προστεθηκε!')
    return redirect(reverse('dashboard:attribute_manager_view', kwargs={'pk': instance.id}))


@method_decorator(staff_member_required, name='dispatch')
class ProductAttriClassManagerView(ListView):
    model = AttributeTitle
    template_name = 'dashboard/ProductAttriClassManager.html'

    def get_queryset(self):
        self.product_attr_class = get_object_or_404(AttributeProductClass, id=self.kwargs['pk'])
        queryset = self.product_attr_class.class_related.my_values.all()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(AttributeProductClass, id=self.kwargs['pk'])
        instance = self.product_attr_class.product_related
        product_attr_class = get_object_or_404(AttributeProductClass, id=self.kwargs['pk'])
        selected_data = product_attr_class.my_attributes.all()
        attr_class = self.product_attr_class
        page_title = 'Διαχείριση Μεγεθολογίου'
        context.update(locals())
        return context


@staff_member_required
def delete_product_attribute_view(request, pk, dk):
    instance = get_object_or_404(Product, pk)
    attribute = get_object_or_404(AttributeClass, id=dk)
    attribute.products.remove(instance)
    attribute.save()
    messages.success(request, 'Το μεγεθολογιο διαγραφηκε')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@method_decorator(staff_member_required, name='dispatch')
class RelatedProductsView(ListView):
    model = Product
    template_name = 'dashboard/product_manager_view.html'

    def get_queryset(self):
        queryset = Product.objects.all()
        search_name = self.request.GET.get('search_name', None)
        if search_name:
            queryset = queryset.filter(title__icontains=search_name)
        queryset = queryset[:20]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(RelatedProductsView, self).get_context_data(**kwargs)
        instance = get_object_or_404(Product, id=self.kwargs['pk'])
        selected_data = instance.related_products.all()
        search_name = self.request.GET.get('search_name', None)
        title = f'Προσθήκη Παρόμοιων Προϊόντων στο {instance.title}'
        table_title, related_product, back_url = 'Παρόμοια Προϊόντα', True, instance.get_edit_url()
        related_product = True
        context.update(locals())
        print('sele', selected_data)
        return context


class ProductWithDifferentColorListView(ListView):
    model = Product
    template_name = 'dashboard/product_manager_view.html'

    def get_queryset(self):
        self.product = get_object_or_404(Product, id=self.kwargs['pk'])
        search_name = self.request.GET.get('search_name', None)
        brand = self.product.brand
        qs = Product.objects.filter(brand=brand) if brand else Product.objects.all()

        if search_name:
            qs = qs.filter(title__icontains=search_name)
        queryset = qs[:20]
        return queryset

    def get_context_data(self, **kwargs):
        color = True
        context = super(ProductWithDifferentColorListView, self).get_context_data(**kwargs)
        instance = self.product
        selected_data = instance.different_color_products.all().exclude(id=instance.id)
        search_name = self.request.GET.get('search_name', None)
        title = f'Προσθήκη Διαφορετικών Χρωματων στο {instance.title}'
        table_title, colors, back_url = 'Παρόμοια Προϊόντα', True, instance.get_edit_url()
        print('here')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoryListView(ListView):
    model = WarehouseCategory
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_queryset(self):
        queryset = WarehouseCategory.filters_data(self.request, WarehouseCategory.objects.all())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = WarehouseCategoryTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        page_title, back_url, create_url = ['Κατηγορίες Αποθήκης', reverse('dashboard:home'),
                                            reverse('dashboard:ware_cate_create_view')
                                            ]
        # filters
        search_filter, active_filter = [True]*2
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoryCreateView(CreateView):
    model = WarehouseCategory
    form_class = WarehouseCategoryForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('dashboard:ware_cate_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = self.success_url, None
        form_title = 'Create new Warehouse Category'
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class WarehouseCategoryUpdateView(UpdateView):
    model = WarehouseCategory
    form_class = WarehouseCategoryForm
    template_name = 'dashboard/form.html'
    success_url = reverse_lazy('dashboard:ware_cate_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, delete_url = self.success_url, self.object.get_delete_url()
        form_title = f'Επεξεργασια {self.object.title}'
        context.update(locals())
        return context


@staff_member_required
def warehouse_category_delete(request, pk):
    instance = get_object_or_404(WarehouseCategory, id=pk)
    instance.delete()
    return redirect('dashboard:ware_cate_list_view')


@method_decorator(staff_member_required, name='dispatch')
class ProductDiscountView(ListView):
    model = ProductDiscount
    template_name = 'dashboard/list_page.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        back_url, create_url, page_title = reverse('dashboard:discount_manager'), \
                                           reverse('dashboard:discount_manager_create'), 'Διαχειριστής Εκπτώσεων'
        queryset_table = ProductDiscountTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ProductDiscountCreateView(CreateView):
    model = ProductDiscount
    form_class = ProductDiscountForm
    template_name = 'dashboard/form.html'

    def get_success_url(self):
        return self.new_instance.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super(ProductDiscountCreateView, self).get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Έκπτωσης', reverse('dashboard:discount_manager')

        context.update(locals())
        return context

    def form_valid(self, form):
        self.new_instance = form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class ProductDiscountUpdateView(UpdateView):
    model = ProductDiscount
    form_class = ProductDiscountForm
    template_name = 'dashboard/discount_manager.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.none()
        if 'search_button' in self.request.GET:
            products = Product.filters_data(self.request, Product.objects.all())
        back_url = reverse('dashboard:discount_manager')
        # filters
        brand_filter, category_filter, search_filter, vendor_filter = [True]*4
        vendors, categories, brands = Vendor.objects.filter(active=True), Category.objects.filter(active=True), Brand.objects.filter(active=True)

        # ajax filter url
        get_params = self.request.get_full_path().split('?', 1)[1] if '?' in self.request.get_full_path() else ''
        ajax_add_url = reverse('dashboard:ajax_products_discount_add', kwargs={'pk': self.object.id}) + '?' + get_params
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class GiftListView(ListView):
    template_name = 'dashboard/list_page.html'
    model = Gifts
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(GiftListView, self).get_context_data(**kwargs)
        context['page_title'] = 'Διαχειριση Δώρων'
        context['back_url'] = reverse('dashboard:home')
        context['create_url'] = reverse('dashboard:gift_create_view')
        context['queryset_table'] = GiftTable(self.object_list)
        return context


@method_decorator(staff_member_required, name='dispatch')
class GiftCreateView(CreateView):
    template_name = 'dashboard/form.html'
    model = Gifts
    form_class = GiftForm

    def get_success_url(self):
        return self.new_instance.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Δημιουργια Δωρου'
        context['back_url'] = reverse('dashboard:gift_list')

        return context

    def form_valid(self, form):
        self.new_instance = form.save()
        return super(GiftCreateView, self).form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)


@method_decorator(staff_member_required, name='dispatch')
class GiftUpdateView(UpdateView):
    template_name = 'dashboard/gift_update_view.html'
    model = Gifts
    form_class = GiftForm
    success_url = reverse_lazy('dashboard:gift_list')

    def form_valid(self, form):
        form.save()
        return super(GiftUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(GiftUpdateView, self).get_context_data(**kwargs)
        context['queryset'] = Product.filters_data(self.request, Product.objects.all())[:30]

        return context


@staff_member_required
def delete_gift_view(request, pk):
    instance = get_object_or_404(Gifts, id=pk)
    instance.delete()
    return redirect(reverse(''))


@method_decorator(staff_member_required, name='dispatch')
class QuickChangeProductWithQtyView(ListView):
    template_name = 'dashboard/quick_change_product_with_qty.html'
    model = Product
    paginate_by = 100

    def get_queryset(self):
        qs = Product.objects.filter(product_class__have_transcations=True)
        return qs

