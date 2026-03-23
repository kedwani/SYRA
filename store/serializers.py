"""
Serializers for the Syra Store API.
"""

from rest_framework import serializers
from django.db.models import F
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.plumbing import build_basic_type
from .models import (
    SyraBandType,
    SyraBandUse,
    SyraBand,
    Order,
    OrderItem,
    Cart,
    CartItem,
    BandRegistration,
    BandReview,
)


class SyraBandTypeSerializer(serializers.ModelSerializer):
    """Serializer for Syra Band Types."""

    class Meta:
        model = SyraBandType
        fields = ["id", "name", "description", "is_active"]
        read_only_fields = ["id"]


class SyraBandUseSerializer(serializers.ModelSerializer):
    """Serializer for Syra Band Uses."""

    class Meta:
        model = SyraBandUse
        fields = ["id", "name", "description", "icon", "is_active"]
        read_only_fields = ["id"]


class SyraBandListSerializer(serializers.ModelSerializer):
    """Serializer for listing Syra Bands."""

    type_name = serializers.CharField(source="band_type.name", read_only=True)
    use_name = serializers.CharField(source="band_use.name", read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = SyraBand
        fields = [
            "id",
            "sku",
            "name",
            "short_description",
            "type_name",
            "use_name",
            "size",
            "color",
            "material",
            "price",
            "discount_price",
            "current_price",
            "has_discount",
            "discount_percentage",
            "stock_quantity",
            "is_available",
            "has_nfc",
            "has_qr_code",
            "has_gps",
            "has_heart_rate",
            "has_water_resistant",
            "battery_life",
            "thumbnail",
            "is_featured",
            "created_at",
        ]


class SyraBandDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Syra Band view."""

    type_name = serializers.CharField(source="band_type.name", read_only=True)
    use_name = serializers.CharField(source="band_use.name", read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_discount = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    band_type = SyraBandTypeSerializer(read_only=True)
    band_use = SyraBandUseSerializer(read_only=True)

    class Meta:
        model = SyraBand
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "short_description",
            "band_type",
            "type_name",
            "band_use",
            "use_name",
            "size",
            "color",
            "material",
            "price",
            "discount_price",
            "current_price",
            "has_discount",
            "discount_percentage",
            "stock_quantity",
            "is_available",
            "allow_preorder",
            "has_nfc",
            "has_qr_code",
            "has_gps",
            "has_heart_rate",
            "has_water_resistant",
            "battery_life",
            "image",
            "thumbnail",
            "is_featured",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SyraBandCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating Syra Bands."""

    band_type_id = serializers.IntegerField(write_only=True)
    band_use_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SyraBand
        fields = [
            "sku",
            "name",
            "description",
            "short_description",
            "band_type_id",
            "band_use_id",
            "size",
            "color",
            "material",
            "price",
            "discount_price",
            "stock_quantity",
            "is_available",
            "allow_preorder",
            "has_nfc",
            "has_qr_code",
            "has_gps",
            "has_heart_rate",
            "has_water_resistant",
            "battery_life",
            "image",
            "thumbnail",
            "is_active",
            "is_featured",
        ]

    def create(self, validated_data):
        band_type_id = validated_data.pop("band_type_id")
        band_use_id = validated_data.pop("band_use_id")

        validated_data["band_type"] = SyraBandType.objects.get(id=band_type_id)
        validated_data["band_use"] = SyraBandUse.objects.get(id=band_use_id)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        band_type_id = validated_data.pop("band_type_id", None)
        band_use_id = validated_data.pop("band_use_id", None)

        if band_type_id:
            instance.band_type = SyraBandType.objects.get(id=band_type_id)
        if band_use_id:
            instance.band_use = SyraBandUse.objects.get(id=band_use_id)

        return super().update(instance, validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Order Items."""

    product_name = serializers.CharField(read_only=True)
    product_sku = serializers.CharField(read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "product_image",
            "quantity",
            "unit_price",
            "discount",
            "total",
            "product_size",
            "product_color",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    @extend_schema_field(build_basic_type(str))
    def get_product_image(self, obj):
        if obj.product.thumbnail:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.product.thumbnail.url)
        return None


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for listing Orders."""

    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "status_display",
            "payment_method",
            "payment_method_display",
            "payment_status",
            "subtotal",
            "shipping_cost",
            "tax_amount",
            "discount_amount",
            "total",
            "created_at",
            "items",
        ]
        read_only_fields = ["id", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed Order view."""

    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "user_name",
            "status",
            "status_display",
            "payment_method",
            "payment_method_display",
            "payment_status",
            "subtotal",
            "shipping_cost",
            "tax_amount",
            "discount_amount",
            "total",
            "shipping_name",
            "shipping_phone",
            "shipping_address",
            "shipping_city",
            "shipping_area",
            "shipping_notes",
            "user_notes",
            "admin_notes",
            "created_at",
            "updated_at",
            "paid_at",
            "shipped_at",
            "delivered_at",
            "items",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Orders."""

    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Order
        fields = [
            "payment_method",
            "shipping_name",
            "shipping_phone",
            "shipping_address",
            "shipping_city",
            "shipping_area",
            "shipping_notes",
            "user_notes",
            "items",
        ]

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        for item in value:
            if "product_id" not in item or "quantity" not in item:
                raise serializers.ValidationError(
                    "Each item must have 'product_id' and 'quantity'."
                )
        return value

    def create(self, validated_data):
        import logging

        logger = logging.getLogger(__name__)

        user = self.context["request"].user
        # Pop user from validated_data to avoid duplicate keyword argument
        validated_data.pop("user", None)
        items_data = validated_data.pop("items")

        # Calculate totals
        from decimal import Decimal
        from django.conf import settings

        subtotal = Decimal("0")
        tax_rate = Decimal(str(settings.STORE_TAX_RATE))
        shipping_cost = Decimal(str(settings.STORE_SHIPPING_COST))

        order_items = []
        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)

            # Validate product exists and is available
            try:
                product = SyraBand.objects.get(id=product_id, is_active=True)
            except SyraBand.DoesNotExist:
                raise serializers.ValidationError(
                    f"Product with ID {product_id} not found or is no longer available."
                )

            # Validate stock availability
            if not product.is_available or product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Product '{product.name}' is not available in requested quantity. "
                    f"Available: {product.stock_quantity}"
                )

            unit_price = product.current_price
            item_total = (unit_price * quantity).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            subtotal += item_total

            order_items.append(
                {
                    "product": product,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": item_total,
                }
            )

        tax_amount = subtotal * tax_rate
        total = subtotal + shipping_cost + tax_amount

        # Use atomic transaction to ensure data consistency
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=user,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                tax_amount=tax_amount,
                total=total,
                **validated_data,
            )

            # Create order items
            # Use atomic stock update to prevent race conditions
            for item in order_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    total=item["total"],
                )

                # Update stock atomically using F() to prevent race conditions
                product = item["product"]
                SyraBand.objects.filter(id=product.id).update(
                    stock_quantity=F("stock_quantity") - item["quantity"]
                )
                # Refresh to get new value
                product.refresh_from_db()

        return order


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for Cart Items."""

    product = SyraBandListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "size",
            "color",
            "total_price",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        cart = self.context["cart"]
        product_id = validated_data.pop("product_id")
        product = SyraBand.objects.get(id=product_id)

        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=validated_data.get("size", "medium"),
            color=validated_data.get("color", "black"),
            defaults=validated_data,
        )

        if not created:
            # Update quantity
            cart_item.quantity += validated_data.get("quantity", 1)
            cart_item.save()

        return cart_item


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart."""

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "total_items",
            "total_price",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class BandRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for Band Registrations."""

    order_item_details = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = BandRegistration
        fields = [
            "id",
            "order_item",
            "order_item_details",
            "public_id",
            "nickname",
            "status",
            "status_display",
            "activated_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(
        {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "product_sku": {"type": "string"},
                "quantity": {"type": "integer"},
            },
        }
    )
    def get_order_item_details(self, obj):
        return {
            "product_name": obj.order_item.product_name,
            "product_sku": obj.order_item.product_sku,
            "quantity": obj.order_item.quantity,
        }


class BandReviewSerializer(serializers.ModelSerializer):
    """Serializer for Band Reviews."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = BandReview
        fields = [
            "id",
            "product",
            "product_name",
            "user",
            "user_username",
            "rating",
            "title",
            "comment",
            "verified_purchase",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "verified_purchase",
            "is_approved",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
