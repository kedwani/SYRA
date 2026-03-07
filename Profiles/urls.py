from django.urls import path
from . import views

urlpatterns = [
    # الرابط الأساسي للسوار
    path("b/<str:bracelet_id>/", views.bracelet_handler, name="bracelet-handler"),
    # سجل المسح
    path("history/", views.scan_history_view, name="scan-history"),
    # الروابط العامة
    path("", views.index, name="index"),
    path("activate/", views.register_medical_info, name="activate"),
    path(
        "view/<str:user__username>/",
        views.ProfileWebView.as_view(),
        name="profile-web-view",
    ),
    # روابط API
    path(
        "api/profile/<str:user__username>/",
        views.ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "api/profile/<str:user__username>/insurance/",
        views.InsuranceDetailView.as_view(),
        name="insurance-detail",
    ),
]
