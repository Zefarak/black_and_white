import django_tables2 as tables

from .models import Post, Photo, PostCategory


class PostTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Επεξεργασία</a>",
                                   orderable=False)

    class Meta:
        model = Post
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'active']


class PostCategoryTable(tables.Table):
    action = tables.TemplateColumn("<a href='{{ record.get_edit_url }}' class='btn btn-primary'>Επεξεργασία</a>",
                                   orderable=False)

    class Meta:
        model = PostCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'active']