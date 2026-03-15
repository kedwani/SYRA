"""URL configuration for SYRA project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.api_urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/store/", include("store.urls")),
    path("", include("accounts.urls")),
    path("", include("profiles.template_urls")),
    path("store/", include("store.template_urls")),
    path("i18n/", include("django.conf.urls.i18n")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
