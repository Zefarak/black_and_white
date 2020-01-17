import django_tables2 as tables

from .models import User, Profile


class UserTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.profile.get_user_edit_url }}' class='btn btn-primary'><i class='fa fa-edit'>"
                                   "</i> </a>", orderable=False, verbose_name='Επεξεργασία'
                                   )

    class Meta:
        model = User
        template_name = 'django_tables2/bootstrap.html'
        fields = ['username', 'email']


class ProfileTable(tables.Table):
    action = tables.TemplateColumn(
        "<a href='{{ record.get_frontend_edit_url }}' class='btn btn-primary'><i class='fa fa-edit'>"
        "</i> </a>", orderable=False, verbose_name='Επεξεργασία'
        )

    class Meta:
        model = Profile
        template_name = 'django_tables2/bootstrap.html'
        fields = ['user_favorite', 'user_title', 'shipping_address']

