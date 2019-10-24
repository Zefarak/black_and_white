from django.views.generic import TemplateView, FormView, ListView, CreateView
from django.contrib import messages
from django.shortcuts import HttpResponseRedirect, reverse, render
from django.urls import reverse_lazy
from site_settings.models import PaymentMethod, Shipping
from .forms import OrderStatusForm
from point_of_sale.models import Order
from contact.models import Contact
from contact.forms import ContactFrontEndForm


def order_status_form_view(request):
    form = OrderStatusForm(request.GET or None)
    if form.is_valid():
        order_code = form.cleaned_data.get('order_code')
        qs = Order.objects.filter(number=order_code) if order_code else Order.objects.none()
        order = qs.first() if qs.exists() else None
        print(order, order_code)
        if order:
            return HttpResponseRedirect(reverse('frontend_order_detail', kwargs={'slug': order.number}))
        else:
            messages.warning(request, 'Δε υπάρχει παραγγελία με αυτόν τον κωδικό')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'frontend/footer_views/order_status_form.html', context={'form': form, })


class PaymentMethodListView(ListView):
    model = PaymentMethod
    template_name = 'frontend/footer_views/payment_policy_view.html'

    def get_queryset(self):
        qs = PaymentMethod.objects.filter(active=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(PaymentMethodListView, self).get_context_data(**kwargs)
        seo_title, keywords, seo_description = 'Τρόποι Πληρωμής', '', ''
        page_title = seo_title
        context.update(locals())


class ShippingListView(ListView):
    model = Shipping
    template_name = 'frontend/footer_views/shipping_policy_view.html'

    def get_queryset(self):
        qs = Shipping.objects.filter(active=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(ShippingListView, self).get_context_data(**kwargs)
        seo_title, keywords, seo_description = 'Τρόποι Αποστολής', '',''
        page_title = seo_title
        context.update(locals())
        return context


class ReturnProductPolicyView(TemplateView):
    template_name = 'frontend/footer_views/return_policy_view.html'


class TermsView(TemplateView):
    template_name = 'frontend/footer_views/rules_view.html'


class CompanyView(TemplateView):
    template_name = 'frontend/footer_views/company_view.html'


class PersonalDataView(TemplateView):
    template_name = 'frontend/footer_views/personal_data.html'


class ContactView(CreateView):
    model = Contact
    form_class = ContactFrontEndForm
    template_name = 'frontend/footer_views/contant_view.html'
    success_url = reverse_lazy('contact_view')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Το μήνυμα σας αποθηκεύτηκε, θα σας απαντήσουμε όσο πιο γρήγορα μπορούμε.')
        return super(ContactView, self).form_valid(form)
