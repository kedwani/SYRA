"""URL configuration for SYRA project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.api_urls')),  # API endpoints
    path('api/profiles/', include('profiles.urls')),
    path('api/store/', include('store.urls')),  # Store API endpoints
    path('', include('accounts.urls')),  # Login, register, logout templates
    path('', include('profiles.template_urls')),  # Dashboard and profile templates
    path('store/', include('store.template_urls')),  # Store templates
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
