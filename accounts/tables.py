import django_tables2 as tables

from .models import User


class UserTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.profile.get_user_edit_url }}' class='btn btn-primary'><i class='fa fa-edit'>"
                                   "</i> </a>", orderable=False, verbose_name='Επεξεργασία'
                                   )

    class Meta:
        model = User
        template_name = 'django_tables2/bootstrap.html'
        fields = ['username', 'email']
