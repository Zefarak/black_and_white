import django_tables2 as tables
from .models import ChartSize


class ChartSizeTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>", verbose_name='Επεξεργασία',
                                   orderable=False
                                   )
    card_ = tables.TemplateColumn("<a href='{{ record.get_card_url }}' class='btn btn-info btn-round'>"
                                   "Καρτελα</a>", verbose_name='Καρτελα',
                                   orderable=False
                                   )
    image = tables.TemplateColumn('<img width="200" height="200" class="img img-responsive" src="{{ record.image.url }}" />')

    class Meta:
        model = ChartSize
        template_name = 'django_tables2/bootstrap.html'
        fields = ['image', 'title', 'brand', 'active']


