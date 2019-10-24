import django_tables2 as tables
from .models import PaymentMethod, Store, Shipping, Banner, SeoDataModel


class PaymentMethodTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = PaymentMethod
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'payment_type', 'active' ]


class StoreTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = PaymentMethod
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'active']


class ShippingTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_additional_cost = tables.Column(orderable=False, verbose_name='Επιπλέον Κόστος')
    tag_limit_value = tables.Column(orderable=False, verbose_name='Μέγιστη Αξία Κόστους')

    class Meta:
        model = Shipping
        template_name = 'django_tables2/bootstrap.html'
        fields = ['ordering_by', 'title', 'tag_additional_cost', 'tag_limit_value', 'active']


class BannerTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )
    tag_image = tables.TemplateColumn(
        "<img class='img-thumbnail' height='200px' width='200px' src='{{ record.image.url }}' />", orderable=False
    )

    class Meta:
        model = Shipping
        template_name = 'django_tables2/bootstrap.html'
        fields = ['tag_image', 'title', 'category', 'active']


class SeoDataTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'><i class='fa fa-edit'></a>",
        orderable=False,
    )

    class Meta:
        model = SeoDataModel
        fields = ['choice' ,'action']

