from django.views.generic import UpdateView, ListView, TemplateView, View, CreateView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.shortcuts import redirect, reverse, render, HttpResponseRedirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string

from django.utils.encoding import force_text, force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth import get_user_model

from accounts.models import Profile, Wishlist
from accounts.tables import ProfileTable
from accounts.forms import LoginForm, SignUpForm, ProfileFrontEndForm, UpdatePasswordForm, ForgotPasswordForm
from accounts.token import account_activation_token
from .tables import UserOrderTable, UserOrderItemTable
from cart.models import CartItem, Cart
from cart.tools import check_or_create_cart
from point_of_sale.models import Order, OrderItem
from catalogue.models import Product

User = get_user_model()

from subscribe.models import Subscribe, UserSubscribe

import io
from reportlab.pdfgen import canvas
from django.http import FileResponse

SITE_EMAIL = settings.SITE_EMAIL


def register_view(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/')
    form_title, form_button = 'Δημιουργια Λογαριασμου', 'Δημιουργια'
    text = '''Δημιουργώντας λογαριασμό στο κατάστημα μας, θα μπορείτε να ολοκληρλωσετε πιο εύκολα την διαδικασία παραγγελίας,
              να προσθέσετε προϊόντα στο λιστα Επιθυμιών και πολλά άλλα.'''
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user_ = form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            send_mail('Ευχαριστουμε που εγγραφήκατε στο simply-you.',
                      f'To username σας είναι {username}',
                      SITE_EMAIL,
                      [username, ],
                      fail_silently=True
                      )
            return redirect('user_profile')
    else:
        messages.warning(request, form.errors)
    context = locals()
    return render(request, 'frontend/user_views/register.html', context)


def login_view(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/')
    login_ = True
    form = LoginForm(request.POST or None)
    form_title, form_button = 'Συνδεση', 'Συνδεση'
    text = 'Εάν έχετε ήδη λογαριασμό, μπορείτε να συνδεθείτε'
    if form.is_valid():
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=raw_password)
        if user:
            login(request, user)
            cart = check_or_create_cart(request)
            if not cart.user:
                cart.user = user
                cart.save()
            return redirect('user_profile')
        else:
            messages.warning(request, 'Ο κωδικός ή το email είναι λάθος.')
    return render(request, 'frontend/user_views/login_or_register.html', context=locals())


def fast_login_view(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=raw_password)
        if user:
            login(request, user)
        else:
            messages.warning(request, 'Ο κωδικός ή το email είναι λάθος.')
    else:
        messages.warning(request, 'Κάτι πήγε λάθος')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email)
        if user:
            print('works!')
        else:
            messages.warning(request, 'Δεν υπάρχει χρήστης με αυτό το email')


def account_activation_sent(request):
    return render(request, 'frontend/user_views/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('homepage')
    else:
        return render(request, 'frontend/user_views/account_activation_invalid.html')


@method_decorator(login_required, name='dispatch')
class UserDashboardView(ListView):
    template_name = 'frontend/user_views/dashboard.html'
    model = Order

    def get_queryset(self):
        profile = self.request.user.profile
        return Order.objects.filter(profile=profile)[:5]

    def get_context_data(self, **kwargs):
        context = super(UserDashboardView, self).get_context_data(**kwargs)
        user = self.request.user
        profile = user.profile
        context.update(locals())
        return context


@login_required
def update_profile_view(request):
    profile = Profile.objects.get(user=request.user)
    form = ProfileFrontEndForm(instance=profile, initial={'user': profile.user})
    if request.POST:
        form = ProfileFrontEndForm(request.POST, instance=profile, initial={'user': profile.user})
        if form.is_valid():
            form.save()
            return redirect('user_profile')

    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'frontend/user_views/user_form.html', context=context)


@login_required
def change_password_view(request):
    if request.POST:
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('user_profile')
        else:
            print('Error')
    else:
        form = UpdatePasswordForm(request.user)
    return render(request, 'frontend/user_views/user_form.html', context={'form': form})


@method_decorator(login_required, name='dispatch')
class UserProfileOrderListView(ListView):
    model = Order
    template_name = 'frontend/user_views/order_list.html'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Order.my_query.get_queryset().eshop_orders_by_user(user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(UserProfileOrderListView, self).get_context_data(**kwargs)
        context['page_title'] = 'Οι παραγγελιες μου'
        context['queryset_table'] = UserOrderTable(self.object_list)
        return context


@method_decorator(login_required, name='dispatch')
class UserCartItemsView(ListView):
    model = OrderItem
    template_name = 'frontend/user_views/order_list.html'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        carts = Order.objects.filter(user=user)
        order_items = OrderItem.objects.filter(order__in=carts)
        return order_items

    def get_context_data(self, **kwargs):
        context = super(UserCartItemsView, self).get_context_data(**kwargs)
        context['page_title'] = 'Ολα Τα Προϊόντα μου'
        context['queryset_table'] = UserOrderItemTable(self.object_list)
        return context


@method_decorator(login_required, name='dispatch')
class WishlistListView(ListView):
    model = Product
    template_name = 'frontend/user_views/wishlist_list.html'
    paginate_by = 15

    def get_queryset(self):
        try:
            wishlist = self.request.user.profile.wishlist
            return wishlist.products.all()
        except:
            return Product.objects.none()


def add_product_to_wishlist_view(request, slug):
    user = request.user
    if not user.is_authenticated:
        messages.warning(request, 'Πρέπει να συνδεθείτε για να προσθέσετε προϊόν')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    profile = user.profile
    wishlist, created = Wishlist.objects.get_or_create(profile_related=profile)
    product = get_object_or_404(Product, slug=slug)
    wishlist.products.add(product)
    wishlist.save()
    messages.success(request, f'Το προϊόν {product} προστέθηκε στην Wish list')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_from_wishlist_view(request, slug):
    user = request.user
    if not user.is_authenticated:
        messages.warning(request, 'Πρέπει να συνδεθείτε για να προσθέσετε προϊόν')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    profile = user.profile
    wishlist, created = Wishlist.objects.get_or_create(profile_related=profile)
    product = get_object_or_404(Product, slug=slug)
    wishlist.products.remove(product)
    wishlist.save()
    messages.success(request, f'Το προϊόν {product} αφαιρεθηκε στην Wish list')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def user_personal_data_view(request):
    return render(request, 'frontend/user_views/personal_data.html')


@login_required
def user_subscription_view(request):
    user = request.user
    subscribes = Subscribe.objects.filter(active=True)
    user_subscribes = user.my_subscribes.all()
    active_subs = user_subscribes.filter(active=True)
    old_user_subs = user_subscribes.filter(active=False)

    return render(request, 'frontend/user_views/user_subscription_page.html', context=locals())


@login_required
def user_subscription_detail_view(request, pk):
    subscription = get_object_or_404(Subscribe, id=pk)

    return render(request, 'frontend/user_views/subscription_detail_view.html', context={'instance': subscription})


@login_required
def pdf_user_data_view(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(30, 750, f'Email {user.email}')
    p.drawString(30, 735, f'Ονοματεπωνυμο {profile.full_name()}, Κινητο: {profile.cellphone}')
    p.drawString(30, 720, f'Διευθυνση: {profile.tag_full_address()}')
    p.drawString(30, 700, f'Στοιχεια που διαθετουμε για τον πελατη {user.username}')

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='personal_data.pdf')


@login_required()
def delete_user_view(request):
    user = request.user
    user.delete()
    messages.warning(request, 'Λυπούμαστε που διαγράψατε τον λογαριασμό σας, ελπίζουμε να μας ξαναπροτιμήσετε στο μέλλον')
    return HttpResponseRedirect('/')


@method_decorator(login_required, name='dispatch')
class UserFavoriteOrderItemsView(ListView):
    template_name = 'frontend/user_views/order_list.html'
    model = OrderItem

    def get_queryset(self):
        qs = OrderItem.objects.filter(order__user=self.request.user, favorite=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(UserFavoriteOrderItemsView, self).get_context_data(**kwargs)
        context['page_title'] = 'Αγαπημενα Προϊόντα'
        context['queryset_table'] = UserOrderItemTable(self.object_list)
        return context


@method_decorator(login_required, name='dispatch')
class UserFavoriteOrderView(ListView):
    template_name = 'frontend/user_views/order_list.html'
    model = Order

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user, favorite_order=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super(UserFavoriteOrderView, self).get_context_data(**kwargs)
        context['page_title'] = 'Αγαπημένες Παραγγελίες'
        context['queryset_table'] = UserOrderTable(self.object_list)
        return context


@method_decorator(login_required, name='dispatch')
class UserShippingListView(ListView):
    template_name = 'frontend/user_views/profiles_list.html'
    model = Profile
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        qs = Profile.objects.filter(user=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset_table'] = ProfileTable(self.object_list)
        return context


@method_decorator(login_required, name='dispatch')
class UserProfileEditView(UpdateView):
    template_name = 'frontend/user_views/user_form.html'
    model = Profile
    form_class = ProfileFrontEndForm
    success_url = reverse_lazy('profiles')

    def get_queryset(self):
        qs = Profile.objects.filter(user=self.request.user)
        return qs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Οι αλλαγες Αποθηκευτηκαν')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class UserProfileCreateView(CreateView):
    template_name = 'frontend/user_views/user_form.html'
    model = Profile
    form_class = ProfileFrontEndForm
    success_url = reverse_lazy('profiles')

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Οι αλλαγες Αποθηκευτηκαν')
        return super().form_valid(form)