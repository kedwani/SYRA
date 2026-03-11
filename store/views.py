"""
Views for the Syra Store API.
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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
from .serializers import (
    SyraBandTypeSerializer,
    SyraBandUseSerializer,
    SyraBandListSerializer,
    SyraBandDetailSerializer,
    SyraBandCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    CartItemSerializer,
    CartSerializer,
    BandRegistrationSerializer,
)


class IsStoreAdmin(IsAdminUser):
    """Permission check for store administrators."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.store_role in [
            "store_admin",
            "product_manager",
            "price_manager",
        ]


class CanManageProducts(IsAuthenticated):
    """Permission to manage products."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.can_manage_products


class CanManagePrices(IsAuthenticated):
    """Permission to manage prices."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.can_manage_prices


class CanViewAnalytics(IsAuthenticated):
    """Permission to view store analytics."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.can_view_store_analytics


class SyraBandTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for Syra Band Types."""

    queryset = SyraBandType.objects.filter(is_active=True)
    serializer_class = SyraBandTypeSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsStoreAdmin()]
        return [AllowAny()]


class SyraBandUseViewSet(viewsets.ModelViewSet):
    """ViewSet for Syra Band Uses."""

    queryset = SyraBandUse.objects.filter(is_active=True)
    serializer_class = SyraBandUseSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsStoreAdmin()]
        return [AllowAny()]


class SyraBandViewSet(viewsets.ModelViewSet):
    """ViewSet for Syra Bands."""

    queryset = SyraBand.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        "band_type__name",
        "band_use__name",
        "size",
        "color",
        "material",
    ]
    search_fields = ["name", "description", "sku"]
    ordering_fields = ["price", "created_at", "is_featured"]
    ordering = ["-is_featured", "-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return SyraBandListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return SyraBandCreateSerializer
        return SyraBandDetailSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanManageProducts()]
        return [AllowAny()]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by featured
        featured = self.request.query_params.get("featured")
        if featured:
            queryset = queryset.filter(is_featured=featured.lower() == "true")

        # Filter by price range
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Filter by availability
        available_only = self.request.query_params.get("available_only")
        if available_only and available_only.lower() == "true":
            queryset = queryset.filter(is_available=True, stock_quantity__gt=0)

        return queryset

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured products."""
        featured_bands = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_bands, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_type(self, request):
        """Get products filtered by type."""
        type_name = request.query_params.get("type")
        if type_name:
            bands = self.queryset.filter(band_type__name=type_name)
            serializer = self.get_serializer(bands, many=True)
            return Response(serializer.data)
        return Response([])

    @action(detail=False, methods=["get"])
    def by_use(self, request):
        """Get products filtered by use case."""
        use_name = request.query_params.get("use")
        if use_name:
            bands = self.queryset.filter(band_use__name=use_name)
            serializer = self.get_serializer(bands, many=True)
            return Response(serializer.data)
        return Response([])


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Orders."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action == "list":
            return OrderListSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order."""
        order = self.get_object()
        if order.status not in ["pending", "processing"]:
            return Response(
                {"error": "Order cannot be cancelled in current status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Restore stock
        for item in order.items.all():
            product = item.product
            product.stock_quantity += item.quantity
            product.save()

        order.status = "cancelled"
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark order as paid (admin only)."""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        order.payment_status = True
        order.status = "processing"
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_status(self, request, pk=None):
        """Update order status (admin only)."""
        if not request.user.is_staff:
            return Response(
                {"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN
            )

        order = self.get_object()
        new_status = request.data.get("status")

        if new_status not in [
            "pending",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "refunded",
        ]:
            return Response(
                {"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.admin_notes = request.data.get("notes", "")
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data)


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for Shopping Cart."""

    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create cart for current user."""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Add item to cart."""
        cart = self.get_object()

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)
        size = request.data.get("size", "medium")
        color = request.data.get("color", "black")

        try:
            product = SyraBand.objects.get(id=product_id, is_active=True)
        except SyraBand.DoesNotExist:
            return Response(
                {"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if not product.is_available and product.stock_quantity < quantity:
            return Response(
                {"error": "Product is not available in requested quantity."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            color=color,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        """Update cart item quantity."""
        cart = self.get_object()

        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND
            )

        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = min(quantity, 10)  # Max 10 items
            cart_item.save()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """Remove item from cart."""
        cart = self.get_object()

        item_id = request.data.get("item_id")

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response(
                {"error": "Item not found in cart."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """Clear all items from cart."""
        cart = self.get_object()
        cart.items.all().delete()

        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Create order from cart."""
        cart = self.get_object()

        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Create order from cart
        subtotal = cart.total_price
        shipping_cost = 50
        tax_rate = 0.14
        tax_amount = subtotal * tax_rate
        total = subtotal + shipping_cost + tax_amount

        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total=total,
            payment_method=request.data.get("payment_method", "cash"),
            shipping_name=request.data.get("shipping_name"),
            shipping_phone=request.data.get("shipping_phone"),
            shipping_address=request.data.get("shipping_address"),
            shipping_city=request.data.get("shipping_city"),
            shipping_area=request.data.get("shipping_area", ""),
            shipping_notes=request.data.get("shipping_notes", ""),
            user_notes=request.data.get("user_notes", ""),
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.current_price,
                total=item.total_price,
            )

            # Update stock
            product = item.product
            product.stock_quantity -= item.quantity
            product.save()

        # Clear cart
        cart.items.all().delete()

        serializer = OrderDetailSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BandRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet for Band Registrations."""

    serializer_class = BandRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return BandRegistration.objects.all()
        return BandRegistration.objects.filter(user=user)

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate a band registration."""
        registration = self.get_object()
        from django.utils import timezone
        from datetime import timedelta

        registration.status = "active"
        registration.activated_at = timezone.now().date()
        registration.expires_at = registration.activated_at + timedelta(days=365)
        registration.save()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a band registration."""
        registration = self.get_object()
        registration.status = "inactive"
        registration.save()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def report_lost(self, request, pk=None):
        """Report a band as lost."""
        registration = self.get_object()
        registration.status = "lost"
        registration.save()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def update_nickname(self, request, pk=None):
        """Update band nickname."""
        registration = self.get_object()
        registration.nickname = request.data.get("nickname", "")
        registration.save()

        serializer = self.get_serializer(registration)
        return Response(serializer.data)
