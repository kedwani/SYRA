"""URL configuration for SYRA project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.api_urls')),  # API endpoints
    path('api/profiles/', include('profiles.urls')),
    path('', include('accounts.urls')),  # Login, register, logout templates
    path('', include('profiles.template_urls')),  # Dashboard and profile templates
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
