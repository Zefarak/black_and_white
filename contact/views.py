from django.shortcuts import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Contact
from .tables import ContactTable
from .forms import ContactForm, ContactFrontEndForm

from django_tables2 import RequestConfig


@method_decorator(staff_member_required, name='dispatch')
class ContactListView(ListView):
    template_name = 'site_settings/list_page.html'
    model = Contact
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = ContactTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)

        #filters data
        search_filter = [True] * 1
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ContactUpdateView(UpdateView):
    template_name = 'site_settings/form.html'
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('contact:contact_list')

    def get_context_data(self, **kwargs):
        context = super(ContactUpdateView, self).get_context_data(**kwargs)
        back_url, form_title = self.success_url, 'Επεξεργασία μηνύματος'
        context.update(locals())
        return context


def validate_frontend_contact_form_view(request):
    contact_form = ContactFrontEndForm(request.POST or None)
    if contact_form.is_valid():
        contact_form.save()
        messages.success(request, 'Το μηνυμά σας εστάλει, θα επικοινωνήσουμε το συντομότερο δυνατόν.')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
