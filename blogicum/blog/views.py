from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    UpdateView,
    ListView,
    CreateView,
    DetailView,
    DeleteView
)

from blogicum.forms import UserUpdateForm
from .models import Post, Category, Comment
from .forms import CreatePostForm, CreateCommentForm
from .mixins import PaginatorListMixin
from .constants import POST_ID_NAME


User = get_user_model()


class BlogListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.published()


class ProfileListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'

    def _get_user(self):
        if not hasattr(self, '_user'):
            username = self.kwargs.get('username', self.request.user.username)
            self._user = get_object_or_404(User, username=username)
        return self._user

    def get_queryset(self):
        url_user = self._get_user()
        current_user = self.request.user

        posts = url_user.posts_author.all()
        if url_user != current_user:
            posts = posts.published()
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self._get_user()
        return context


class CategoryListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/category.html'

    def _get_category(self):
        if hasattr(self, '_category'):
            return self._category

        category_slug = self.kwargs.get('category_slug')
        self._category = get_object_or_404(
            Category, slug=category_slug, is_published=True)
        return self._category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self._get_category()
        return context

    def get_queryset(self):
        category = self._get_category()
        return Post.objects.in_category(category)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = CreatePostForm

    def get_success_url(self):
        username = self.request.user.username
        return reverse('blog:profile', kwargs={'username': username})

    def form_valid(self, form):
        form.instance.author_id = self.request.user.pk
        return super().form_valid(form)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = Post.objects.available_for_user(self.request.user)

        obj = super().get_object(queryset=queryset)

        if obj is None:
            raise Http404('Вы не можете просматривать этот пост')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        if not hasattr(self, '_post'):
            post_id = self.kwargs.get('pk')
            self._post = get_object_or_404(Post, pk=post_id)
        return self._post

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        post = self.get_object()
        # Перенаправляем на страницу деталей поста, если пользователь не автор
        return redirect('blog:post_detail', pk=post.pk)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreatePostForm(instance=self.object)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs[POST_ID_NAME]
        return reverse('blog:post_detail', kwargs={'pk': post_id})

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        post_id = self.kwargs[POST_ID_NAME]
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


@login_required
def add_comment(request, pk):
    user = request.user
    post = get_object_or_404(Post.objects.available_for_user(user), pk=pk)
    form = CreateCommentForm(request.POST)

    if not form.is_valid():
        return redirect('blog:post_detail', pk=pk)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()

    return redirect('blog:post_detail', pk=pk)
