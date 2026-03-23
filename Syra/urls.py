"""URL configuration for SYRA project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/accounts/", include("accounts.api_urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/store/", include("store.urls")),
    path("", include("accounts.urls")),
    path("", include("profiles.template_urls")),
    path("store/", include("store.template_urls")),
    # Legal pages
    path(
        "privacy/",
        TemplateView.as_view(template_name="legal/privacy.html"),
        name="privacy",
    ),
    path(
        "terms/", TemplateView.as_view(template_name="legal/terms.html"), name="terms"
    ),
    path(
        "support/",
        TemplateView.as_view(template_name="legal/support.html"),
        name="support",
    ),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
