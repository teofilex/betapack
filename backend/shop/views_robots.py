from django.http import HttpResponse
from django.views.decorators.http import require_GET


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
