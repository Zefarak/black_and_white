from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import reverse
from .models import User
from accounts.tables import UserTable
from .tables import OrderEshopMiniTable
from subscribe.tables import UserSubscribeMiniTable


@method_decorator(staff_member_required, name='dispatch')
class UserListView(ListView):
    model = User
    template_name = 'point_of_sale/order-list.html'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['create_button'] = reverse('point_of_sale:user_list_view')
        context['queryset_table'] = UserTable(self.object_list)
        context['page_title'] = 'Χρηστες'
        return context


@method_decorator(staff_member_required, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = 'point_of_sale/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        orders = self.object.orders.all()
        subscribes = self.object.my_subscribes.all()
        context['orders_queryset'] = OrderEshopMiniTable(orders)
        context['subs_queryset'] = UserSubscribeMiniTable(subscribes)
        return context
