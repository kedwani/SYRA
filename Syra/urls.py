from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Import the function views directly
from Accounts.template_views import login_view, register_view, logout_view
from Profiles.template_views import (
    dashboard_view,
    emergency_view,
    search_view,
    edit_profile_view,
)

# We use the 'web' namespace to match your redirects (e.g., redirect("web:dashboard"))
web_patterns = (
    [
        path("", dashboard_view, name="home"),  # Or a specific landing page
        path("login/", login_view, name="login"),
        path("register/", register_view, name="register"),
        path("logout/", logout_view, name="logout"),
        path("dashboard/<str:username>/", dashboard_view, name="dashboard"),
        path("edit/<str:username>/", edit_profile_view, name="edit_profile"),
        path("search/", search_view, name="search"),
        path("emergency/<uuid:public_id>/", emergency_view, name="emergency"),
    ],
    "web",
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # ── HTML Template Views (with 'web' namespace) ─────────────────
    path("", include(web_patterns)),
    # ── DRF API ────────────────────────────────────────────────────
    path("api/auth/", include("Accounts.urls")),
    path("api/profile/", include("Profiles.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
