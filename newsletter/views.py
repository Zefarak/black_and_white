from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import ListView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import reverse, get_object_or_404, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
from site_settings.tools import queryset_to_workbook
from django_tables2 import RequestConfig

from .models import NewsLetter
from .tables import NewsLetterTable
from .forms import NewsLetterForm


@method_decorator(staff_member_required, name='dispatch')
class NewsLetterListView(ListView):
    model = NewsLetter
    template_name = 'site_settings/list_page.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(NewsLetterListView, self).get_context_data(**kwargs)
        queryset_table = NewsLetterTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        back_url, create_url = reverse('dashboard:home'), reverse('newsletter:create')
        download, download_url = True, reverse('newsletter:download_newsletter')
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class NewsLetterUpdateView(UpdateView):
    model = NewsLetter
    template_name = 'site_settings/form.html'
    form_class = NewsLetterForm

    def get_success_url(self):
        return reverse('newsletter:list')

    def get_context_data(self, **kwargs):
        context = super(NewsLetterUpdateView, self).get_context_data(**kwargs)
        back_url, delete_url = self.get_success_url(), self.object.get_delete_url
        form_title = f'Επεξεργασία... {self.object} '
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super(NewsLetterUpdateView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class NewsLetterCreateView(CreateView):
    model = NewsLetter
    form_class = NewsLetterForm
    template_name = 'site_settings/form.html'

    def get_success_url(self):
        return reverse('newsletter:list')

    def get_context_data(self, **kwargs):
        context = super(NewsLetterCreateView, self).get_context_data(**kwargs)
        form_title, back_url = 'δημιουργία Newsletter', reverse('newsletter:list')

        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super(NewsLetterCreateView, self).form_valid(form)


@staff_member_required
def delete_newsletter_view(request, pk):
    newsletter = get_object_or_404(NewsLetter, id=pk)
    newsletter.delete()
    return redirect(reverse('newsletter:list'))


@staff_member_required
def download_newsletter_view(request):
    qs = NewsLetter.objects.filter(confirm=True)
    columns = ('email', 'first_name', 'last_name', 'gender')
    workbook = queryset_to_workbook(qs, columns)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="export.xls"'
    workbook.save(response)
    return response


def validate_frontend_newsletter_view(request):
    form = NewsLetterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, f"Το {form.cleaned_data['email']} "
                                  f"προστέθηκε στην λίστα με τα newsletter, Σας ευχαριστούμε.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
