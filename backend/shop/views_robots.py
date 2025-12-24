from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.contrib.sitemaps.views import sitemap as django_sitemap


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /cart",
        "Disallow: /checkout",
        "",
        f"Sitemap: https://betapack-production.up.railway.app/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_view(request, sitemaps, **kwargs):
    """
    Custom sitemap view koji ne dodaje X-Robots-Tag: noindex header
    """
    response = django_sitemap(request, sitemaps, **kwargs)

    # Ukloni X-Robots-Tag header ako postoji
    if 'X-Robots-Tag' in response:
        del response['X-Robots-Tag']

    return response
