import django_tables2 as tables

from .models import Subscribe, UserSubscribe


class SubscribeTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = Subscribe
        template_name = 'django_tables2/bootstrap.html'
        fields = ['id', 'title', 'category', 'action', 'active']


class UserSubscribeTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>",
                                   orderable=False
                                   )
    tag_value = tables.Column(orderable=False, verbose_name='Αξία')
    duration = tables.Column(orderable=False, verbose_name='Διάρκεια')

    class Meta:
        model = UserSubscribe
        template_name = 'django_tables2/bootstrap.html'
        fields = ['subscription', 'user', 'tag_value', 'duration', 'active']
