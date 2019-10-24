from django.views.generic import ListView, UpdateView, CreateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, reverse
from django_tables2 import RequestConfig

from .models import ChartSize
from catalogue.product_details import Brand
from catalogue.categories import Category
from catalogue.models import Product
from .tables import ChartSizeTable
from .mixins import FormMixin


@method_decorator(staff_member_required, name='dispatch')
class ChartSizeListView(ListView):
    model = ChartSize
    template_name = 'site_settings/list_page.html'
    paginate_by = 20

    def get_queryset(self):
        qs = ChartSize.objects.all()
        qs = ChartSize.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset_table = ChartSizeTable(self.object_list)
        RequestConfig(self.request).configure(queryset_table)
        page_title, create_url, back_url = ['Size Chart', reverse('size_chart:create'),
                                            reverse('site_settings:dashboard')]
        search_filter, active_filter = [True]*2

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ChartSizeCreateView(FormMixin, CreateView):

    def get_context_data(self, **kwargs):
        context = super(ChartSizeCreateView, self).get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία', self.success_url
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class ChartSizeUpdateView(FormMixin, UpdateView):

    def get_context_data(self, **kwargs):
        context = super(ChartSizeUpdateView, self).get_context_data(**kwargs)
        form_title, back_url, delete_url = f'Επεξεργασία {self.object}', self.success_url, self.object.get_delete_url()

        context.update(locals())
        return context


@staff_member_required
def chart_size_delete_view(request, pk):
    chart_size = get_object_or_404(ChartSize, id=pk)
    chart_size.delete()
    return redirect(reverse('size_chart:list'))


@method_decorator(staff_member_required, name='dispatch')
class ChartSizeManagerView(DetailView):
    model = ChartSize
    template_name = 'chart_size/manager_view.html'

    def get_context_data(self, **kwargs):
        context = super(ChartSizeManagerView, self).get_context_data(**kwargs)
        brands = Brand.objects.filter(active=True)
        categories = Category.objects.filter(active=True)
        products = Product.filters_data(self.request, Product.my_query.active_for_site())[:15]

        search_filter, brand_filter = [True] * 2
        context.update(locals())
        return context
