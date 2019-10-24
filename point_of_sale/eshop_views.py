from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.core.mail import send_mail
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.shortcuts import HttpResponseRedirect
from django_tables2 import RequestConfig

from .models import Order, OrderProfile, SendReceipt
from .tables import OrderEshopTable
from .forms import EshopOrderStatusForm, OrderProfileForm, SendReceiptForm
from site_settings.constants import ORDER_STATUS
from accounts.models import User
import datetime
from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class EshopOrderListView(ListView):
    template_name = 'point_of_sale/eshop_views/list-view.html'
    model = Order
    paginate_by = 30

    def get_queryset(self):
        qs = Order.my_query.get_queryset().eshop_orders()
        qs = Order.eshop_orders_filtering(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(EshopOrderListView, self).get_context_data(**kwargs)
        queryset_table = OrderEshopTable(self.object_list)
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(queryset_table)

        #  filter
        order_status = ORDER_STATUS
        search_filter, date_filter, order_status_filter = [True] * 3
        # date filter
        date_now = datetime.datetime.now() - relativedelta(month=6)
        date_now, date_end = date_now.strftime('%m/%d/%Y'), datetime.datetime.now().strftime('%m/%d/%Y')
        date_range = self.request.GET.get('daterange', f'{date_now} - {date_end}')
        context.update(locals())
        return context


class EshopOrderDetailView(DetailView):
    model = Order
    template_name = 'point_of_sale/eshop_views/detail_view.html'

    def get_context_data(self, **kwargs):
        context = super(EshopOrderDetailView, self).get_context_data(**kwargs)
        order_profile, created = OrderProfile.objects.get_or_create(order_related=self.object)
        form = EshopOrderStatusForm(initial={'status': self.object.status})
        context.update(locals())
        return context


@staff_member_required
def create_user_view(request, pk):
    profile = get_object_or_404(OrderProfile, id=pk)
    email = profile.email
    user, created = User.objects.get_or_create(username=email)
    if created:
        user.first_name = profile.first_name
        user.last_name = profile.last_name
        user.email = email
        user.password = User.objects.make_random_password()
        user.save()

    order = profile.order_related
    order.user = user
    order.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def eshop_order_edit_profile(request, pk):
    profile = get_object_or_404(OrderProfile, id=pk)
    form = OrderProfileForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect(profile.order_related.get_eshop_url())
    return render(request, 'point_of_sale/form.html', context={'form': form,
                                                               'form_title': 'Επεξεργασία Προφίλ',
                                                               'back_url': profile.order_related.get_eshop_url()
                                                               })


@method_decorator(staff_member_required, name='dispatch')
class CreateShippingVoucher(CreateView):
    model = SendReceipt
    form_class = SendReceiptForm
    template_name = 'point_of_sale/form.html'

    def get_initial(self):
        self.order = get_object_or_404(Order, id=self.kwargs['pk'])
        initial = super(CreateShippingVoucher, self).get_initial()
        initial['order_related'] = self.order
        initial['email'] = self.order.guest_email
        initial['shipping_method'] = self.order.shipping_method
        return initial

    def get_success_url(self):
        self.order = get_object_or_404(Order, id=self.kwargs['pk'])
        return self.order.get_eshop_url()

    def get_context_data(self, **kwargs):
        context = super(CreateShippingVoucher, self).get_context_data(**kwargs)
        page_title = 'Δημιουργία Voucher'
        back_url = self.get_success_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        order = get_object_or_404(Order, id=self.kwargs['pk'])
        voucher = form.save()
        send_mail('Αποστολή',
                  f'Η απόστολή σας παραδόθηκε στο courrier, με κωδικό {voucher.shipping_code}',
                  'my_email@gmail.com',
                  [order.guest_email, ],
                  fail_silently=True
                  )
        order.status = '8'
        order.save()
        return super(CreateShippingVoucher, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class EditShippingVoucher(UpdateView):
    model = SendReceipt
    form_class = SendReceiptForm
    template_name = 'point_of_sale/form.html'

    def get_success_url(self):
        order = self.object.order_related
        return order.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super(EditShippingVoucher, self).get_context_data(**kwargs)
        form_title, back_url = 'Επεξεργασία', self.get_success_url()

        context.update(locals())
        return context