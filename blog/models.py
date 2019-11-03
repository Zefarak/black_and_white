from django.db import models
from django.shortcuts import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from tinymce.models import HTMLField

import slugify


def upload_image(instance, filename):
    return f'blog/{instance.post_related.id}/{filename}'


class Post(models.Model):
    status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(unique=True, max_length=220)
    image = models.ImageField(upload_to='blog/')
    text = HTMLField(blank=True)
    slug = models.SlugField(blank=True, allow_unicode=True)

    def __str__(self):
        return self.title

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
        slug = slugify.slugify(instance.title)
        qs = Post.objects.filter(slug=slug)
        if qs.exists():
            slug = slug + '-'+ instance.id
        instance.slug = slug
        instance.save()


class YouTubeVideo(models.Model):
    url = models.URLField()
    post_related = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post_related}- {self.id}'


class Photo(models.Model):
    post_related = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to=upload_image,)
