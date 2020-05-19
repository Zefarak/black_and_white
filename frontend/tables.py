import django_tables2 as tables

from point_of_sale.models import Order, OrderItem


class UserOrderTable(tables.Table):
    remove = tables.TemplateColumn(
        "<a href='{{ record.get_remove_favorite_url }}' "
        "{% if record.favorite_order %} class='btn btn-warning' {% else %} class='btn btn-success' {% endif %}>"
        "{% if record.favorite_order %} <i class='fa fa-minus'></i> {% else %} <i class='fa fa-plus'></i> {% endif %}"
        "</a>",
        orderable=False, verbose_name='Αφαιρεση από Αγαπημένη')
    action = tables.TemplateColumn("<a href='{{ record.get_frontend_detail_url }}' class='btn btn-info'><i class='fa fa-edit'></i></a>",
                                   orderable=False, verbose_name='Επεξεργασια')
    full_address = tables.Column(orderable=False, verbose_name='Διευθυνση')
    tag_final_value = tables.Column(orderable=False, verbose_name='Αξία')

    class Meta:
        attrs = {'class': 'table .table-hover table-responsive'}
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'title', 'full_address', 'tag_final_value', 'status']


class UserOrderItemTable(tables.Table):
    action = tables.TemplateColumn(
        "<a data-href='{% url 'ajax_show_order_item' record.id %}' class='btn btn-round btn-success order_item_detail'>"
        "<i class='fa fa-edit'></i>"
        "</a>",
        orderable=False, verbose_name='Λεπτομέριες')
    remove = tables.TemplateColumn(
        "<a href='{{ record.get_add_or_remove_favorite_url }}' class='btn btn-info'>"
        "{% if record.favorite %} <i class='fa fa-minus'></i> {% else %} <i class='fa fa-plus'></i> {% endif %}</a>",
        orderable=False, verbose_name='Αγαπημενα Προϊόντα')

    tag_final_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = OrderItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['timestamp', 'title','qty', 'tag_final_value']
