"""
URL configuration for the Syra Store template views.
"""

from django.urls import path
from . import template_views

app_name = "store"

urlpatterns = [
    # Store home
    path("", template_views.store_home, name="home"),
    # Products
    path("bands/", template_views.band_list, name="band_list"),
    path("bands/<int:band_id>/", template_views.band_detail, name="band_detail"),
    # Cart
    path("cart/", template_views.cart_view, name="cart"),
    path("cart/add/<int:band_id>/", template_views.add_to_cart, name="add_to_cart"),
    path(
        "cart/update/<int:item_id>/",
        template_views.update_cart_item,
        name="update_cart_item",
    ),
    path(
        "cart/remove/<int:item_id>/",
        template_views.remove_from_cart,
        name="remove_from_cart",
    ),
    # Checkout
    path("checkout/", template_views.checkout, name="checkout"),
    # Orders
    path("orders/", template_views.order_list, name="order_list"),
    path("orders/<int:order_id>/", template_views.order_detail, name="order_detail"),
    path(
        "orders/<int:order_id>/cancel/",
        template_views.order_cancel,
        name="order_cancel",
    ),
    # My Bands
    path("my-bands/", template_views.my_bands, name="my_bands"),
    path(
        "my-bands/<int:reg_id>/activate/",
        template_views.registration_activate,
        name="registration_activate",
    ),
    path(
        "my-bands/<int:reg_id>/report-lost/",
        template_views.registration_report_lost,
        name="registration_report_lost",
    ),
    path(
        "my-bands/<int:reg_id>/update-nickname/",
        template_views.registration_update_nickname,
        name="registration_update_nickname",
    ),
    # AJAX endpoints
    path("api/cart-count/", template_views.get_cart_count, name="cart_count"),
    path("api/filter-bands/", template_views.filter_bands, name="filter_bands"),
]
