"""URL configuration for the Accounts API."""

from django.urls import path
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.views import TokenRefreshView
from . import views


def login_redirect(request):
    """Redirect /accounts/login/ to / with next parameter preservation."""
    next_url = request.GET.get("next", "/")
    return HttpResponseRedirect(f"/?next={next_url}")


urlpatterns = [
    # Template views (HTML pages)
    path("", views.login_template_view, name="login"),
    path("accounts/login/", login_redirect, name="login_redirect"),
    path("register/", views.register_template_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
]
