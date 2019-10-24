from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.generic import DetailView, CreateView, UpdateView
from django.shortcuts import HttpResponseRedirect, get_object_or_404, render
from django.shortcuts import redirect, reverse
from accounts.models import Profile
from accounts.forms import ProfileForm
from .models import Order, OrderItem, OrderProfile, SendReceipt
from voucher.models import Voucher
from .forms import OrderCreateCopyForm, OrderProfileForm, SendReceiptForm, VoucherForm
from site_settings.models import PaymentMethod, Company
from catalogue.models import Product
import datetime


@staff_member_required
def auto_create_retail_order(request, action):
    # action can be sell, return,
    profile, created = Profile.objects.get_or_create(first_name='Πελατες', last_name='Λιανικής')
    payment_method, created_ = PaymentMethod.objects.get_or_create(title='Μετρητά')
    new_instance = Order.objects.create(
        date_expired=datetime.datetime.now(),
        title='Retail',
        profile=profile,
    )
    if action == 'sell':
        new_instance.title = f'Πώληση... {new_instance.id}'
        new_instance.order_type = 'r'
    if action == 'eshop':
        new_instance.order_type = 'e'
    if action == 'return':
        new_instance.title = f'Επιστροφή...{new_instance.id}'
        new_instance.order_type = 'b'
        new_instance.status = '5'
    if action == 'ware_income':
        new_instance.title = f'Παραστατικό Εισαγωγής'
        new_instance.order_type = 'wa'
    if action == 'ware_outcome':
        new_instance.title = f'Παραστατικό Εξαγωγής'
        new_instance.order_type = 'wr'
    new_instance.payment_method = payment_method
    new_instance.save()
    new_instance.refresh_from_db()
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
    response = redirect(new_instance.get_edit_url())
    response.set_cookie('order_redirect', 'homepage')
    return response


@staff_member_required
def quick_pay_costumer_view(request, pk):
    instance = get_object_or_404(Profile, id=pk)
    instance.value = 0
    instance.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@staff_member_required
def done_order_view(request, pk, action):
    instance = get_object_or_404(Order, id=pk)
    order_items = instance.order_items.exists()
    if not order_items:
        instance.delete()
        return redirect(reverse('point_of_sale:home'))
    if action == 'paid':
        instance.is_paid = True
        instance.status = "8"
    instance.save()
    return redirect(reverse('point_of_sale:order_list'))


@staff_member_required
def create_copy_order(request, pk):
    instance = get_object_or_404(Order, id=pk)
    form_title, back_url = f'Αντιγραφή {instance.title}', reverse('point_of_sale:order_list')
    form = OrderCreateCopyForm(request.POST or None)
    if form.is_valid():
        order_type = form.cleaned_data.get('order_type', instance.order_type)
        new_instance = Order.objects.get(id=pk)
        new_instance.pk = None
        new_instance.date_expired = datetime.datetime.now()
        new_instance.order_type = order_type
        new_instance.save()
        new_instance.refresh_from_db()
        for order_item in instance.order_items.all():
            new_order_item = OrderItem.objects.get(id=order_item.id)
            new_order_item.pk = None
            new_order_item.order = new_instance
            new_order_item.save()
        return redirect(new_instance.get_edit_url())

    context = locals()
    return render(request, 'dashboard/form.html', context)


@method_decorator(staff_member_required, name='dispatch')
class OrderPrintView(DetailView):
    model = Order
    template_name = 'point_of_sale/print_page.html'

    def get_context_data(self, **kwargs):
        context = super(OrderPrintView, self).get_context_data(**kwargs)
        order_items = self.object.order_items.all()
        company = Company.objects.first() if Company.objects.exists() else None
        profile, created = OrderProfile.objects.get_or_create(order_related=self.object)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CreateCostumerFromOrder(CreateView):
    model = Profile
    template_name = 'point_of_sale/form.html'
    form_class = ProfileForm

    def get_success_url(self):
        invoice = get_object_or_404(Order, id=self.kwargs['pk'])
        return invoice.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Πελάτη', self.get_success_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        new_costumer = form.save()
        invoice = get_object_or_404(Order, id=self.kwargs['pk'])
        invoice.profile = new_costumer
        invoice.save()
        return super(CreateCostumerFromOrder, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class EditCostumerFromOrder(CreateView):
    model = Profile
    template_name = 'point_of_sale/form.html'
    form_class = ProfileForm

    def get_success_url(self):
        invoice = get_object_or_404(Order, id=self.kwargs['pk'])
        return invoice.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form_title, back_url = 'Δημιουργία Πελάτη', self.get_success_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        new_costumer = form.save()
        invoice = get_object_or_404(Order, id=self.kwargs['pk'])
        invoice.profile = new_costumer
        invoice.save()
        return super(CreateCostumerFromOrder, self).form_valid(form)


@staff_member_required
def order_change_costumer(request, pk, dk):
    order = get_object_or_404(Order, id=pk)
    new_costumer = get_object_or_404(Profile, id=dk)
    old_costumer = order.profile
    order.profile = new_costumer
    order.save()
    if old_costumer:
        old_costumer.refresh_from_db()
        old_costumer.save()
    return HttpResponseRedirect(order.get_edit_url())


@method_decorator(staff_member_required, name='dispatch')
class ProfileOrderDetailView(UpdateView):
    model = OrderProfile
    form_class = OrderProfileForm
    template_name = 'point_of_sale/form.html'


    def get_success_url(self):
        instance = self.object.order_related
        return instance.get_edit_url()

    def get_context_data(self, **kwargs):
        context = super(ProfileOrderDetailView, self).get_context_data(**kwargs)
        form_title, back_url = 'Επεξεργασία Προφίλ', self.get_success_url()
        context.update(locals())
        return context

    def form_valid(self, form):
        form.save()
        return super(ProfileOrderDetailView, self).form_valid(form)


@staff_member_required
def create_or_edit_order_voucher_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    if not order.order_type == 'e':
        return HttpResponseRedirect(order.get_edit_url())
    voucher, created = SendReceipt.objects.get_or_create(order_related=order)
    if created:
        voucher.email = order.profile.email
        voucher.shipping_method = order.shipping
        voucher.save()

    form = SendReceiptForm(request.POST or None, instance=voucher)
    if form.is_valid():
        form.save()
        messages.success(request, f'Στάλθηκε email sto {voucher.email} με κωδικό {voucher.shipping_code}')
        return HttpResponseRedirect(order.get_edit_url())
    return render(request, 'point_of_sale/shipping_voucher.html', locals())


@staff_member_required
def order_voucher_manager_view(request, pk):
    order = get_object_or_404(Order, id=pk)
    back_url = order.get_edit_url()
    vouchers = order.vouchers.all()

    form = VoucherForm(request.POST or None)
    if form.is_valid():
        title = form.cleaned_data.get('title')
        qs = Voucher.objects.filter(code=title.upper(), active=True)
        voucher = qs.first() if qs.exists() else None
        if not voucher:
            is_available, message = False, 'Δεν υπάρχει κουπόνι με αυτόν τον κωδικό'
            messages.warning(request, message)
            print(is_available, message)
            return HttpResponseRedirect(reverse('point_of_sale:voucher_manager', kwargs={'pk': pk}))
        is_available, message = voucher.check_if_its_available(order, request.user, voucher)
        if not is_available:
            messages.warning(request, message)
            print('result', message)
            return HttpResponseRedirect(reverse('point_of_sale:voucher_manager', kwargs={'pk': pk}))
        benefit_value = voucher.calculate_discount_value(order)

        print('result', benefit_value, message)
        return HttpResponseRedirect(reverse('point_of_sale:voucher_manager', kwargs={'pk': pk}))

    '''
        is_available, message = Voucher.is_available_to_user(order, voucher, order.profile.user)
        if not is_available:
            messages.warning(request, message)
            return redirect(reverse('point_of_sale:voucher_manager', kwargs={'pk': pk}))

        if voucher_rule.exclusive and len(vouchers)>0:
            messages.warning(request, 'Δε μπορείτε να προσθέσετε αυτόο το κουπόνι.')
        order.vouchers.add(voucher)

        order_items = order.order_items.all()
        for order_item in order_items:
            have_benefit = voucher_rule.gets_benefit(order_item)
            if have_benefit:
                pass
    '''

    context = {
        'form': form,
        'vouchers': vouchers,
        'back_url': back_url
    }

    return render(request, 'point_of_sale/action_pages/voucher_manager.html', context)


