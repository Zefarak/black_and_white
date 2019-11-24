from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, TemplateView, UpdateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from .models import Post, PostCategory
from .tables import PostTable, PostCategoryTable
from .forms import PostForm, PostCategoryForm


class BlogHomepageView(ListView):
    template_name = 'blog/blog_categories.html'
    model = PostCategory
    paginate_by = 10

    def get_queryset(self):
        qs = PostCategory.objects.filter(active=True)
        return qs


class CategoryDetailView(ListView):
    template_name = 'blog/homepage.html'
    model = Post
    paginate_by = 10

    def get_queryset(self):
        self.category = get_object_or_404(PostCategory, slug=self.kwargs['slug'])
        qs = Post.objects.filter(status=True, category=self.category)
        print(qs.count())
        return qs

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        context['category'] = self.category
        return context


class BlogDetailView(DetailView):
    template_name = 'blog/detail_view.html'
    model = Post


@method_decorator(staff_member_required, name='dispatch')
class BlogListView(ListView):
    template_name = 'blog/dashboard/dashboard_list_view.html'
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
    template_name = 'blog/dashboard/dashboard_detail_view.html'
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
    template_name = 'blog/dashboard/form_view.html'
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


@method_decorator(staff_member_required, name='dispatch')
class PostCategoryListView(ListView):
    model = PostCategory
    template_name = 'site_settings/list_page.html'

    def get_queryset(self):
        qs = PostCategory.objects.all()
        qs = PostCategory.filter_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Κατηγοριες Blog'
        context['back_url'] = reverse('site_settings:dashboard')
        context['queryset_table'] = PostCategoryTable(self.object_list)
        return context


@method_decorator(staff_member_required, name='dispatch')
class PostCategoryCreateView(CreateView):
    model = PostCategory
    form_class = PostCategoryForm
    template_name = 'site_settings/form.html'
    success_url = reverse_lazy('blog:post_category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Δημιουργια Κατηγοριας Blog'
        context['back_url'] = self.success_url
        return context

    def form_valid(self, form):
        form.save()
        return super(PostCategoryCreateView, self).form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class PostCategoryUpdateView(UpdateView):
    model = PostCategory
    form_class = PostCategoryForm
    success_url = reverse_lazy('blog:post_category_list')
    template_name = 'site_settings/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Επεξεργασια {self.object}'
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        return context

    def form_valid(self, form):
        form.save()
        return super(PostCategoryUpdateView, self).form_valid(form)


@staff_member_required
def post_category_delete_view(request, pk):
    instance = get_object_or_404(PostCategory, id=pk)
    instance.delete()
    return redirect(reverse('blog:post_category_list'))



class BlogCategoryListView(ListView):
    template_name = 'blog/blog_categories.html'
    model = PostCategory

    def get_queryset(self):
        qs = PostCategory.objects.filter(active=True)
        print('hello world!')
        return qs