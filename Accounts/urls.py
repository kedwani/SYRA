"""URL configuration for the Accounts API."""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Template views (HTML pages)
    path('', views.login_template_view, name='login'),
    path('register/', views.register_template_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
