from django.shortcuts import get_object_or_404,HttpResponseRedirect
from django.contrib import messages
from site_settings.models import SiteSettings
from functools import wraps


def site_active(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        site_setting = get_object_or_404(SiteSettings, id=1)
        if not site_setting.is_open:
            messages.warning(request, 'Το κατάστημά μας είναι κλειστό αυτή την στιγμή')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return function(request, *args, **kwargs)
    return wrap
