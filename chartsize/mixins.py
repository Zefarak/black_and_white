from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import ChartSize
from .forms import ChartSizeForm


class FormMixin(FormView):
    model = ChartSize
    template_name = 'site_settings/form.html'
    success_url = reverse_lazy('size_chart:list')
    form_class = ChartSizeForm

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Η ενέργεια σας αποθηκεύτηκε')
        return super().form_valid(form)