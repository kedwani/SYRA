"""
URL configuration for SYRA medical app.
"""

from django.urls import path
from apps.medical import views

app_name = 'medical'

urlpatterns = [
    # Medical data endpoints (ViewSet routes handled in main urls.py)
    # These are included via the router
]