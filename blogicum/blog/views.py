from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet

from django.http import Http404
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
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


User = get_user_model()


class BlogListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        now = timezone.now()
        # Фильтруем записи:
        # опубликованные и с датой публикации не позднее текущего времени
        return Post.objects.filter(is_published=True,
                                   pub_date__lte=now,
                                   category__is_published=True
                                   )


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
        if url_user == current_user:
            return Post.objects.filter(author=url_user)
        else:
            now = timezone.now()
            return Post.objects.filter(
                (Q(author=url_user)
                 & Q(is_published=True)
                 & Q(category__is_published=True)
                 & Q(pub_date__lte=now)
                 )
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self._get_user()
        return context


class CategoryListView(PaginatorListMixin, ListView):
    model = Post
    template_name = 'blog/category.html'

    def _get_category(self):
        if not hasattr(self, '_category'):
            category_slug = self.kwargs.get('category_slug')
            self._category = get_object_or_404(
                Category, slug=category_slug, is_published=True)
        return self._category

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self._get_category()
        return context

    def get_queryset(self):
        now = timezone.now()
        category = self._get_category()
        return Post.objects.filter(category=category,
                                   is_published=True,
                                   pub_date__lte=now)


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
        # здесь объект, который должен быть отображен
        obj = super().get_object(queryset=queryset)

        now = timezone.now()

        if (not obj.is_published
            or not obj.category.is_published
                or obj.pub_date > now) and obj.author != self.request.user:
            # Если пользователь не автор и пост не опубликован,
            # показываем 404 ошибку
            raise Http404('Вы не можете просматривать этот пост')

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreateCommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


'''class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        post_id = self.kwargs.get('pk')
        return get_object_or_404(Post, pk=post_id)

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)
'''


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        # Сохраняем объект для использования в других методах
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


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CreatePostForm(instance=self.object)
        return context

    def get_object(self, queryset=None):
        post_id = self.kwargs.get('pk')
        user_id = self.request.user.pk
        return get_object_or_404(Post, pk=post_id, author=user_id)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CreateCommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def get_object(self, queryset=None):
        comment_id = self.kwargs['comment_id']
        user_id = self.request.user.pk

        return get_object_or_404(Comment, pk=comment_id, author=user_id)


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_id})

    def get_object(self, queryset=None):
        # Получаем ID комментария из аргументов URL
        comment_id = self.kwargs['comment_id']
        user_id = self.request.user.pk

        return get_object_or_404(Comment, pk=comment_id, author=user_id)


@login_required
def add_comment(request, pk):
    # Получаем объект дня рождения или выбрасываем 404 ошибку.
    post = get_object_or_404(Post, pk=pk)
    form = CreateCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)

        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('blog:post_detail', pk=pk)
