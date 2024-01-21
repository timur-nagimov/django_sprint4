from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPage(TemplateView):
    template_name = 'pages/about.html'


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Возвращает страницу с ошибкой 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Возвращает страницу с ошибкой 500."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Возвращает страницу с ошибкой 403(csrf)."""
    return render(request, 'pages/403csrf.html', status=403)
