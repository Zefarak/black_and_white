from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse_lazy, reverse

from .models import Subscribe, UserSubscribe
from .forms import SubscribeForm, UserSubscribeForm
from .tables import SubscribeTable, UserSubscribeTable


@method_decorator(staff_member_required, name='dispatch')
class SubscribeHomepageView(TemplateView):
    template_name = 'subscribe/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscribes'] = Subscribe.objects.filter(active=True)
        context['user_subs'] = UserSubscribe.objects.all()[:10]
        return context


@method_decorator(staff_member_required, name='dispatch')
class SubscribeListView(ListView):
    template_name = 'subscribe/list_view.html'
    model = Subscribe

    def get_context_data(self, **kwargs):
        context = super(SubscribeListView, self).get_context_data(**kwargs)
        context['queryset_table'] = SubscribeTable(self.object_list)
        context['page_title'] = 'Subscribes'
        context['create_url'] = reverse('subscribe:subscribe_create')
        context['back_url'] = reverse('subscribe:homepage')
        return context


@method_decorator(staff_member_required, name='dispatch')
class SubscribeCreateView(CreateView):
    template_name = 'subscribe/form_view.html'
    model = Subscribe
    form_class = SubscribeForm
    success_url = reverse_lazy('subscribe:subscribe_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Δημιουργια τύπου Subscribe'
        context['back_url'] = self.success_url

        return context
    
    def form_valid(self, form):
        form.save()
        return super(SubscribeCreateView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class SubscribeUpdateView(UpdateView):
    template_name = 'subscribe/form_view.html'
    model = Subscribe
    form_class = SubscribeForm
    success_url = reverse_lazy('subscribe:subscribe_list_view')
    
    def get_context_data(self, **kwargs):
        context = super(SubscribeUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = f'επεξεργασια {self.object}'
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        return context
    
    def form_valid(self, form):
        form.save()
        return super(SubscribeUpdateView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
def delete_subscribe_view(request, pk):
    instance = get_object_or_404(Subscribe, id=pk)
    instance.delete()
    return redirect(reverse('subscribe:subscribe_list_view'))


@method_decorator(staff_member_required, name='dispatch')
class UserSubscribeListView(ListView):
    template_name = 'subscribe/list_view.html'
    model = UserSubscribe
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Subscribes Χρήστων'
        context['back_url'] = reverse('subscribe:homepage')
        context['create_url'] = reverse('subscribe:user_subscribe_create')
        context['queryset_table'] = UserSubscribeTable(self.object_list)
        return context


@method_decorator(staff_member_required, name='dispatch')
class UserSubscribeCreateView(CreateView):
    template_name = 'subscribe/form_view.html'
    model = UserSubscribe
    form_class = UserSubscribeForm
    success_url = reverse_lazy('subscribe:user_subscribe_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Δημιουργια Νεου User Subscription'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class UserSubscribeUpdateView(UpdateView):
    template_name = 'subscribe/form_view.html'
    form_class = UserSubscribeForm
    model = UserSubscribe
    success_url = reverse_lazy('subscribe:user_subscribe_list_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Επεξεργασια {self.object}'
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        return context


@staff_member_required
def delete_user_subscribe_view(request, pk):
    instance = get_object_or_404(UserSubscribe, id=pk)
    instance.delete()
    return redirect(reverse('subscribe:user_subscribe_list_view'))

