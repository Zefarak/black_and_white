from django.utils.html import format_html
import django_tables2 as tables

from accounts.models import Profile
from .models import Order, OrderItem


class ProfileTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'><i class='fa fa-edit'>"
                                   "</i> </a>", orderable=False, verbose_name='Επεξεργασία'
                                   )
    tag_balance = tables.Column(orderable=False, verbose_name='Υπόλοιπο')
    pay = tables.TemplateColumn("<a href='{% url 'point_of_sale:costumer_pay' record.id %}' class='btn btn-success'>"
                                "Πληρωμή</a> ", orderable=False, verbose_name='Γρήγορη Πληρωμή')
    card_ = tables.TemplateColumn("<a href='{{ record.get_card_url }}' class='btn btn-info btn-round'>"
                                "Καρτέλα</a> ", orderable=False, verbose_name='Καρτέλες')

    class Meta:
        model = Profile
        template_name = 'django_tables2/bootstrap.html'
        fields = ['first_name', 'last_name', 'profile_type', 'cellphone', 'tag_balance']


class OrderTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}?next={{ request.get_full_path|urlencode }}'"
                                   " class='btn btn-{{ record.paid_color }}'><i class='fa fa-edit'></i></a>",
                                   orderable=False
                                   )
    tag_final_value = tables.Column(orderable=False, verbose_name='Αξία')
    tag_status = tables.TemplateColumn("<p class='table-{{ record.table_color }}'>{{ record.get_status_display }}</p>",
                                       verbose_name='Κατάσταση')
    tag_profile_full_name = tables.Column(verbose_name='Στοιχεία Χρήστη', orderable=False)
    tag_address = tables.Column(verbose_name='Διεύθυνση', orderable=False)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired', 'tag_profile_full_name',
                  'tag_address', 'order_type',
                  'tag_final_value', 'tag_status', 'action'
                  ]


class OrderEshopTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_eshop_url }}?next={{ request.get_full_path|urlencode }}'"
                                   " class='btn btn-{{ record.paid_color }}'><i class='fa fa-edit'></i></a>",
                                   orderable=False
                                   )
    tag_final_value = tables.Column(orderable=False, verbose_name='Αξία')

    tag_profile_full_name = tables.Column(verbose_name='Στοιχεία Χρήστη', orderable=False)
    tag_address = tables.Column(verbose_name='Διεύθυνση', orderable=False)

    class Meta:
        model = Order
        template_name = 'django_tables2/bootstrap-responsive.html'
        fields = ['date_expired', 'tag_profile_full_name', 'tag_address',
                  'payment_method', 'shipping_method', 'tag_final_value', 'status'
                  ]
        attrs = {
            'class': 'small table table-sm table-striped table-hover'
        }


class OrderItemListTable(tables.Table):
    get_date = tables.Column(orderable=False, verbose_name='Ημερομηνία')

    class Meta:
        model = OrderItem
        template_name = 'django_tables2/bootstrap.html'
        fields = ['get_date', 'title', 'qty', 'tag_final_value', 'tag_total_value']
