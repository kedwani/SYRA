"""
Admin configuration for the Syra Store.
"""

from django.contrib import admin
from .models import (
    SyraBandType,
    SyraBandUse,
    SyraBand,
    Order,
    OrderItem,
    Cart,
    CartItem,
    BandRegistration,
)


@admin.register(SyraBandType)
class SyraBandTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(SyraBandUse)
class SyraBandUseAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "icon", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]


@admin.register(SyraBand)
class SyraBandAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "sku",
        "band_type",
        "band_use",
        "price",
        "stock_quantity",
        "is_available",
        "is_featured",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "is_featured",
        "is_available",
        "band_type",
        "band_use",
        "size",
        "color",
        "material",
    ]
    search_fields = ["name", "sku", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("Basic Info", {"fields": ("sku", "name", "description", "short_description")}),
        (
            "Band Details",
            {"fields": ("band_type", "band_use", "size", "color", "material")},
        ),
        ("Pricing", {"fields": ("price", "discount_price")}),
        ("Stock", {"fields": ("stock_quantity", "is_available", "allow_preorder")}),
        (
            "Features",
            {
                "fields": (
                    "has_nfc",
                    "has_qr_code",
                    "has_gps",
                    "has_heart_rate",
                    "has_water_resistant",
                    "battery_life",
                )
            },
        ),
        ("Images", {"fields": ("image", "thumbnail")}),
        (
            "Status",
            {"fields": ("is_active", "is_featured", "created_at", "updated_at")},
        ),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ["product", "quantity", "unit_price", "discount", "total"]
    can_delete = False
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "status",
        "payment_method",
        "payment_status",
        "total",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "payment_status", "created_at"]
    search_fields = ["order_number", "user__username", "user__email"]
    readonly_fields = [
        "order_number",
        "created_at",
        "updated_at",
        "paid_at",
        "shipped_at",
        "delivered_at",
    ]
    inlines = [OrderItemInline]
    fieldsets = (
        (
            "Order Info",
            {
                "fields": (
                    "order_number",
                    "user",
                    "status",
                    "payment_method",
                    "payment_status",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "subtotal",
                    "shipping_cost",
                    "tax_amount",
                    "discount_amount",
                    "total",
                )
            },
        ),
        (
            "Shipping",
            {
                "fields": (
                    "shipping_name",
                    "shipping_phone",
                    "shipping_address",
                    "shipping_city",
                    "shipping_area",
                    "shipping_notes",
                )
            },
        ),
        ("Notes", {"fields": ("user_notes", "admin_notes")}),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "paid_at",
                    "shipped_at",
                    "delivered_at",
                )
            },
        ),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "created_at", "updated_at"]
    search_fields = ["user__username", "user__email"]


@admin.register(BandRegistration)
class BandRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "order_item",
        "public_id",
        "nickname",
        "status",
        "activated_at",
        "expires_at",
    ]
    list_filter = ["status", "activated_at"]
    search_fields = ["user__username", "public_id", "nickname"]
    readonly_fields = ["public_id", "created_at", "updated_at"]
