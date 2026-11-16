from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.sitemaps.views import sitemap as django_sitemap


@require_GET
def robots_txt(request):
    # API domen nije sajt: nema stranica za pretragu. Sitemap sajta se servira
    # sa www domena (Vercel rewrite), pa ovde nema Sitemap linije.
    lines = [
        "User-agent: *",
        "Disallow: /",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")


def sitemap_view(request, sitemaps, **kwargs):
    """
    Custom sitemap view koji ne dodaje X-Robots-Tag: noindex header
    """
    response = django_sitemap(request, sitemaps, **kwargs)

    # Ukloni X-Robots-Tag header ako postoji
    if 'X-Robots-Tag' in response:
        del response['X-Robots-Tag']

    return response
