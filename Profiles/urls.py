from django.urls import path
from .views import ProfileDetailView, InsuranceDetailView

urlpatterns = [
    path(
        "profile/<str:user__username>/",
        ProfileDetailView.as_view(),
        name="profile-detail",
    ),
    path(
        "profile/<str:user__username>/insurance/",
        InsuranceDetailView.as_view(),
        name="insurance-detail",
    ),
]
