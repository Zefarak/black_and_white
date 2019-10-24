import django_tables2 as tables

from .models import NewsLetter


class NewsLetterTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary btn-round'>"
                                   "<i class='fa fa-edit'> </i></a>",
                                   orderable=False
                                   )

    class Meta:
        model = NewsLetter
        fields = ['email', 'confirmed', 'timestamp']
        template_name = 'django_tables2/bootstrap.html'
