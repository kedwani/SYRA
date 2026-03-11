"""
URL configuration for the Syra Store API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SyraBandTypeViewSet, SyraBandUseViewSet, SyraBandViewSet,
    OrderViewSet, CartViewSet, BandRegistrationViewSet
)

router = DefaultRouter()
router.register(r'types', SyraBandTypeViewSet, basename='band-type')
router.register(r'uses', SyraBandUseViewSet, basename='band-use')
router.register(r'bands', SyraBandViewSet, basename='band')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'registrations', BandRegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]
