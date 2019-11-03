from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import Post
from .tables import PostTable
from .forms import PostForm


class BlogHomepageView(ListView):
    template_name = 'blog/homepage.html'
    model = Post
    paginate_by = 10


class BlogDetailView(DetailView):
    template_name = 'blog/detail_view.html'
    model = Post


@method_decorator(staff_member_required, name='dispatch')
class BlogListView(ListView):
    template_name = 'blog/dashboard_list_view.html'
    model = Post
    paginate_by = 20

    def get_queryset(self):
        queryset = Post.objects.all()
        queryset = Post.filter_data(self.request, queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(BlogListView, self).get_context_data(**kwargs)
        context['queryset_table'] = PostTable(self.object_list)
        context['create_url'] = reverse('dashboard_blog:create_view')
        context['back_url'] = reverse('dashboard:home')
        context['search_filter'], context['active_filter'] = [True]*2
        return context


@method_decorator(staff_member_required, name='dispatch')
class PostUpdateView(UpdateView):
    template_name = 'blog/dashboard_detail_view.html'
    model = Post
    form_class = PostForm
    success_url = reverse_lazy('dashboard_blog:list_view')

    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = f'Επεξεργασια {self.object}'
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        return context

    def form_valid(self, form):
        form.save()

        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/form_view.html'
    success_url = reverse_lazy('dashboard_blog:list_view')

    def get_success_url(self):
        return self.new_instance.get_edit_url()

    def form_valid(self, form):
        self.new_instance = form.save()
        return super(CreatePostView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CreatePostView, self).get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['page_title'] = 'Δημιουργια Νέου Post'

        return context


@staff_member_required
def delete_post_view(request, pk):
    instance = get_object_or_404(Post, id=pk)
    instance.delete()
    return redirect(reverse('dashboard_blog:list_view'))








