"""
Views for SYRA store app.
Handles e-commerce product listings and orders.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

from apps.store.models import Product, Order, OrderItem
from apps.store.serializers import (
    ProductSerializer, ProductListSerializer, OrderSerializer
)
from apps.store.serializers import OrderCreateSerializer


class ProductListView(APIView):
    """List all active products."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        products = Product.objects.filter(status=Product.STATUS_ACTIVE)
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            products = products.filter(category=category)
        
        # Filter by type
        product_type = request.query_params.get('type')
        if product_type:
            products = products.filter(product_type=product_type)
        
        # Featured only
        if request.query_params.get('featured') == 'true':
            products = products.filter(is_featured=True)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    """Get product detail."""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug, status=Product.STATUS_ACTIVE)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class OrderListView(APIView):
    """List user's orders or create a new order."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            items_data = serializer.validated_data['items']
            subtotal = 0
            
            order = Order.objects.create(
                user=request.user,
                customer_email=serializer.validated_data['customer_email'],
                customer_phone=serializer.validated_data['customer_phone'],
                shipping_name=serializer.validated_data['shipping_name'],
                shipping_address=serializer.validated_data['shipping_address'],
                shipping_city=serializer.validated_data['shipping_city'],
                shipping_postal_code=serializer.validated_data.get('shipping_postal_code', ''),
                shipping_country=serializer.validated_data.get('shipping_country', 'Egypt'),
                payment_method=serializer.validated_data['payment_method'],
                notes=serializer.validated_data.get('notes', ''),
                status=Order.STATUS_PENDING,
            )
            
            for item_data in items_data:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 1)
                
                product = get_object_or_404(Product, id=product_id, status=Product.STATUS_ACTIVE)
                
                if product.track_inventory:
                    if not product.allow_oversell and product.quantity < quantity:
                        return Response(
                            {'error': f'Insufficient stock for {product.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    product.quantity -= quantity
                    product.save()
                
                item_total = product.price * quantity
                subtotal += item_total
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    name=product.name,
                    sku=product.sku,
                    quantity=quantity,
                    price=product.price,
                    total=item_total
                )
            
            shipping_cost = 0 if subtotal >= 50000 else 3500
            tax = int((subtotal + shipping_cost) * 0.14)
            
            order.subtotal = subtotal
            order.shipping_cost = shipping_cost
            order.tax = tax
            order.total = subtotal + shipping_cost + tax
            order.save()
        
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(APIView):
    """Get order detail."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderCancelView(APIView):
    """Cancel an order."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        
        if order.status not in [Order.STATUS_PENDING, Order.STATUS_PAID]:
            return Response(
                {'error': 'Order cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Restore inventory
        for item in order.items.all():
            if item.product and item.product.track_inventory:
                item.product.quantity += item.quantity
                item.product.save()
        
        order.status = Order.STATUS_CANCELLED
        order.save()
        
        return Response({'message': 'Order cancelled successfully'})