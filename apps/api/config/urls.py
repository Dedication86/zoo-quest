"""
Zoo Quest URL map.

/admin/            Django Admin (MVP admin dashboard)
/api/v1/           Public explorer API + health
/api/schema/       OpenAPI schema (feeds the TypeScript client)
/api/docs/         Swagger UI (local only)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

api_v1 = [
    path("", include("apps.core.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.play.urls")),
    # M5: path("", include("apps.analytics.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include((api_v1, "v1"), namespace="v1")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]

if settings.DEBUG:
    urlpatterns += [path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs")]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "Zoo Quest"
admin.site.site_title = "Zoo Quest admin"
admin.site.index_title = "Manage your zoo"
