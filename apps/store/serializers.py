"""
Serializers for SYRA store app.
"""

from rest_framework import serializers
from apps.store.models import Product, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    """
    
    price_formatted = serializers.CharField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'product_type', 'category', 'price', 'price_formatted',
            'compare_at_price', 'compare_at_price_formatted',
            'sku', 'quantity', 'track_inventory', 'allow_oversell',
            'status', 'image', 'images', 'weight', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for product listings.
    """
    
    price_formatted = serializers.CharField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'price',
            'price_formatted', 'compare_at_price', 'image', 'in_stock'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for OrderItem model.
    """
    
    price_formatted = serializers.CharField(read_only=True)
    total_formatted = serializers.CharField(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'name', 'sku', 'quantity', 'price', 'price_formatted',
            'total', 'total_formatted'
        ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for Order model.
    """
    
    items = OrderItemSerializer(many=True, read_only=True)
    total_formatted = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'customer_email', 'customer_phone',
            'shipping_name', 'shipping_address', 'shipping_city',
            'shipping_postal_code', 'shipping_country',
            'subtotal', 'shipping_cost', 'tax', 'total', 'total_formatted',
            'payment_method', 'payment_status', 'transaction_id',
            'status', 'notes', 'created_at', 'updated_at',
            'paid_at', 'shipped_at', 'delivered_at', 'items'
        ]
        read_only_fields = [
            'id', 'subtotal', 'shipping_cost', 'tax', 'total',
            'payment_status', 'transaction_id', 'created_at',
            'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating orders.
    """
    
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)
    shipping_name = serializers.CharField(max_length=200)
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20, required=False)
    shipping_country = serializers.CharField(max_length=50, default='Egypt')
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField()
        )
    )


class CartItemSerializer(serializers.Serializer):
    """
    Serializer for cart items.
    """
    
    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    name = serializers.CharField(read_only=True)
    price = serializers.IntegerField(read_only=True)
    total = serializers.IntegerField(read_only=True)