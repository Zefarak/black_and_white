from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django.contrib.admin.views.decorators import staff_member_required

from .models import Post, Photo
from .forms import PostPhotoUploadForm

@staff_member_required
def ajax_delete_photo(request, pk):
    photo = get_object_or_404(Photo, id=pk)
    post = photo.post_related
    photo.delete()
    data = dict()
    data['result'] = render_to_string(request=request,
                                      template_name='blog/ajax_views/result_container.html',
                                      context={
                                          'object': post
                                      })
    return JsonResponse(data)


@staff_member_required
def ajax_add_images(request, pk):
    instance = get_object_or_404(Post, id=pk)
    form = PostPhotoUploadForm()
    data = dict()
    if request.POST:
        form = PostPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = Photo.objects.create(post_related=instance,
                                         image=form.cleaned_data.get('image'))
            data = {
                'is_valid': True,
                'name': photo.post_related.title,
                'url': photo.image.url
            }
    instance.refresh_from_db()
    data['result'] = render_to_string(template_name='blog/ajax_views/result_container.html',
                                      request=request,
                                      context={
                                          'object': instance
                                      }
                                    )
    return JsonResponse(data)
