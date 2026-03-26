"""
URL configuration for SYRA hardware app.
"""

from django.urls import path
from apps.hardware import views

app_name = 'hardware'

urlpatterns = [
    # Bracelet management (ViewSet routes handled in main urls.py)
]