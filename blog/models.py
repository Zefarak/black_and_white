from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from tinymce.models import HTMLField
from django.utils.text import slugify


def upload_image(instance, filename):
    return f'blog/{instance.post_related.id}/{filename}'


class PostCategory(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατασταση')
    title = models.CharField(unique=True, max_length=200, verbose_name='Τιτλος')
    image = models.ImageField(upload_to='blog/categories/', verbose_name='Εικονα')
    slug = models.SlugField(allow_unicode=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:category_detail_view', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('dashboard_blog:post_category_update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('dashboard_blog:post_category_delete', kwargs={'pk': self.id})

    @staticmethod
    def filter_data(request, qs):
        search_name = request.GET.get('search_name', None)
        active_name = request.GET.get('active_name', None)

        qs = qs.filter(active=True) if active_name else qs
        qs = qs.filter(title__icontains=search_name) if search_name else qs
        return qs


@receiver(post_save, sender=PostCategory)
def create_post_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        if not instance.slug:
            new_slug = slugify(instance.title, allow_unicode=True)
            qs_exists = PostCategory.objects.filter(slug=new_slug).exists()
            instance.slug = f'{new_slug}-{instance.id}' if qs_exists else new_slug
            instance.save()


class Post(models.Model):
    show_first_page = models.BooleanField(default=False, verbose_name='Εμφανιση Πρωτη Σελιδα')
    status = models.BooleanField(default=False, verbose_name='Κατασταση')
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(blank=True, null=True, verbose_name='Ημερομηνια')
    title = models.CharField(unique=True, max_length=220, verbose_name='Ονομασια')
    image = models.ImageField(upload_to='blog/posts/main/', verbose_name='Εικονα')
    text = HTMLField(blank=True, verbose_name='Κειμενο')
    slug = models.SlugField(blank=True, allow_unicode=True)
    show_custom_date = models.BooleanField(default=False, verbose_name='Χρησιμοποιησε την ημερομηνια')
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, verbose_name='Κατηγορια')

    def __str__(self):
        return self.title

    def tag_date(self):
        if self.show_custom_date and self.date:
            return self.date
        return self.timestamp

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'slug': self.slug})

    def get_edit_url(self):
        return reverse('dashboard_blog:update_view', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('dashboard_blog:delete_view', kwargs={'pk': self.id})

    @staticmethod
    def filter_data(request, queryset):
        search_name = request.GET.get('search_name', None)
        active_name = request.GET.get('active_name', None)
        queryset = queryset.filter(active=True) if active_name == '1' else queryset.filter(active_name=False) if active_name == '2' else queryset
        queryset = queryset.filter(Q(title__contains=search_name) |
                                   Q(text__contains=search_name)).distinct() if search_name else queryset
        return queryset


@receiver(post_save, sender=Post)
def create_slug(sender, instance, **kwargs):
    if not instance.slug:
        slug = slugify(instance.title, allow_unicode=True)
        qs = Post.objects.filter(slug=slug)
        if qs.exists():
            slug = slug + '-'+ instance.id
        instance.slug = slug
        instance.save()


class YouTubeVideo(models.Model):
    url = models.TextField(blank=True)
    post_related = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='my_videos')

    def __str__(self):
        return f'{self.post_related}- {self.id}'


class Photo(models.Model):
    post_related = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=upload_image)
