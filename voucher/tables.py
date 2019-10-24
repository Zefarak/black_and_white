import django_tables2 as tables
from .models import Voucher
from catalogue.categories import Category
from catalogue.models import Product
from catalogue.product_details import Brand


class VoucherTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Voucher
        fields = ['name', 'code', 'usage', 'start_date', 'end_date', 'active', 'action']
        template_name = 'django_tables2/bootstrap.html'


class VoucherProductForSelectTable(tables.Table):
    action = tables.TemplateColumn(
        "<a data-href='' "
        "class='btn btn-primary btn-round plus_button'><i class='fa fa-plus'> </i></a>",
        orderable=False
    )

    class Meta:
        model = Product
        fields = ['title']
        template_name = 'django_tables2/bootstrap.html'


class VoucherCategoryTable(tables.Table):
    action = tables.TemplateColumn("<a data-href='{% url 'vouchers:ajax_voucher_category' voucher.id record.id 'add' %}'"
                                   " class='btn btn-primary btn-round plus_button'>"
                                   "<i class='fa fa-plus'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Category
        fields = ['name']
        template_name = 'django_tables2/bootstrap.html'


class VoucherBrandTable(tables.Table):
    action = tables.TemplateColumn("<a data-href='' class='btn btn-primary btn-round plus_button'>"
                                   "<i class='fa fa-plus'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Brand
        fields = ['title']
        template_name = 'django_tables2/bootstrap.html'


class ProductSelectedDataTable(tables.Table):
    action = tables.TemplateColumn("<a data-href='' class='btn btn-primary btn-round delete_button'>"
                                   "<i class='fa fa-remove'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Product
        fields = ['title']
        template_name = 'django_tables2/bootstrap.html'


class CategorySelectedDataTable(tables.Table):
    action = tables.TemplateColumn("<a data-href='{% url 'vouchers:ajax_voucher_category' voucher.id record.id 'delete' %}'"
                                   " class='btn btn-danger btn-round delete_button'>"
                                   "<i class='fa fa-trash'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Category
        fields = ['name', ]
        template_name = 'django_tables2/bootstrap.html'


class BrandSelectedDataTable(tables.Table):
    action = tables.TemplateColumn("<a data-href='' class='btn btn-primary btn-round delete_button'>"
                                   "<i class='fa fa-remove'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Brand
        fields = ['title', ]
        template_name = 'django_tables2/bootstrap.html'
