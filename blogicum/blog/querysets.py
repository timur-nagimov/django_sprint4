from django.db import models
from django.utils import timezone
from django.db.models import Q


class PostQuerySet(models.QuerySet):

    def published(self):
        now = timezone.now()
        return self.filter(is_published=True,
                           pub_date__lte=now,
                           category__is_published=True)

    def in_category(self, category):
        return self.published().filter(category=category)

    def available_for_user(self, user, queryset=None):
        if queryset is None:
            queryset = self

        now = timezone.now()
        if user.is_authenticated:
            return queryset.filter(
                Q(is_published=True,
                  category__is_published=True,
                  pub_date__lte=now)
                | Q(author=user)
            )
        return queryset.published()
