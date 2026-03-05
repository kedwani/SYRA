from django.urls import path
from . import views
from .views import ProfileDetailView, InsuranceDetailView, ProfileWebView

urlpatterns = [
    # رابط العرض للمتصفح (زي اللي هيفتح من الـ QR Code)
    path(
        "view/<str:user__username>/", ProfileWebView.as_view(), name="profile-web-view"
    ),
    # روابط الـ API للبيانات
    path(
        "api/profile/<str:user__username>/",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "api/profile/<str:user__username>/insurance/",
        InsuranceDetailView.as_view(),
        name="insurance-detail",
    ),
    path("", views.index, name="index"),
    path("activate/", views.register_medical_info, name="activate"),
]
