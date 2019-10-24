import django_tables2 as tables

from .models import Contact


class ContactTable(tables.Table):
    action = tables.TemplateColumn('<a href="{{ record.get_edit_url }}" class="btn btn-primary">'
                                   '<i class="fa fa-edit"></></a>',
                                   orderable=False)

    class Meta:
        model = Contact
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'timestamp', 'email', 'is_readed', 'action']