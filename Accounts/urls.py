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
    # Verification views
    path("verify/email/<str:token>/", views.verify_email_view, name="verify_email"),
    path("verify/phone/", views.verify_phone_view, name="verify_phone"),
    path("resend-otp/", views.resend_otp_view, name="resend_otp"),
    # Admin views - using /manage/ prefix to avoid conflict with Django admin
    path(
        "manage/doctors/",
        views.admin_doctor_approvals_view,
        name="admin-doctor-approvals",
    ),
    path("manage/approve-doctor/", views.approve_doctor_view, name="approve-doctor"),
    path("manage/reject-doctor/", views.reject_doctor_view, name="reject-doctor"),
    path(
        "manage/doctor/<int:doctor_id>/", views.doctor_detail_view, name="doctor-detail"
    ),
    path("manage/revoke-doctor/", views.revoke_doctor_view, name="revoke-doctor"),
]
