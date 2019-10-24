import django_tables2 as tables
from .models import Cart
from catalogue.models import Product


class CartTable(tables.Table):
    action = tables.TemplateColumn('<a href="{{ record.get_edit_url }}" class="btn btn-info btn-round">'
                                   '<i class="fa fa-info"></> </a>', orderable=False
                                   )
    final_value = tables.TemplateColumn("<p> {{record.tag_final_value}} </p>")
    status = tables.TemplateColumn("<p "
                                   "{% if record.status == 'Submitted' %}"
                                   " style='background-color: #d1efc2' "
                                   "{% else %}"
                                   "{% endif %}>{{ record.get_status_display }}</p>"
                                   )
    cart_id = tables.TemplateColumn('<p>{{ record.cart_id|truncatechars_html:15 }}')

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        model = Cart
        fields = ['timestamp', 'cart_id', 'shipping_method', 'payment_method', 'final_value', 'status']


class ProductCartTable(tables.Table):
    action = tables.TemplateColumn("<a href='' class='btn btn-info'><i class='fa fa-edit'> </i></a>", orderable=False)
    tag_final_price = tables.Column(orderable=False)

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        model = Product
        fields = ['sku', 'title', 'qty', 'vendor', 'category', 'tag_final_price']


class CartItemTable(tables.Table):
    actions = tables.TemplateColumn("<a hfre='' class='btn btn-warning'><i class='fa fa-edit'></i></a> ")

    class Meta:
        template_name = 'django_tables2/bootstrap.html'
        model = Product
        fields = ['sku', 'title', 'qty', 'vendor', 'category', 'tag_final_price']
