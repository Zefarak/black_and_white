import django_tables2 as tables

from .product_details import Vendor


class VendorTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></i></a>",
                                   orderable=False,
                                   )

    class Meta:
        model = Vendor
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'phone']
