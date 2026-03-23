"""Unit tests for the Store app."""

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from store.models import (
    SyraBandType,
    SyraBandUse,
    SyraBand,
    Order,
    OrderItem,
    Cart,
    CartItem,
    BandReview,
)

SyraUser = get_user_model()


class SyraBandTypeModelTest(TestCase):
    """Tests for the SyraBandType model."""

    def test_create_band_type(self):
        """Test creating a band type."""
        band_type = SyraBandType.objects.create(
            name="classic", description="Classic Syra Band", is_active=True
        )
        self.assertEqual(band_type.name, "classic")
        self.assertEqual(band_type.get_name_display(), "Classic")
        self.assertTrue(band_type.is_active)

    def test_band_type_str_representation(self):
        """Test string representation of band type."""
        band_type = SyraBandType.objects.create(name="premium")
        self.assertEqual(str(band_type), "Premium")

    def test_unique_name(self):
        """Test that name must be unique."""
        SyraBandType.objects.create(name="standard")
        with self.assertRaises(Exception):
            SyraBandType.objects.create(name="standard")

    def test_default_is_active(self):
        """Test that is_active defaults to True."""
        band_type = SyraBandType.objects.create(name="kids")
        self.assertTrue(band_type.is_active)


class SyraBandUseModelTest(TestCase):
    """Tests for the SyraBandUse model."""

    def test_create_band_use(self):
        """Test creating a band use case."""
        band_use = SyraBandUse.objects.create(
            name="personal",
            description="Personal health tracking",
            icon="heart",
            is_active=True,
        )
        self.assertEqual(band_use.name, "personal")
        self.assertEqual(band_use.get_name_display(), "Personal Health")

    def test_band_use_str_representation(self):
        """Test string representation of band use."""
        band_use = SyraBandUse.objects.create(name="child")
        self.assertEqual(str(band_use), "Child Safety")

    def test_unique_name(self):
        """Test that name must be unique."""
        SyraBandUse.objects.create(name="personal")
        with self.assertRaises(Exception):
            SyraBandUse.objects.create(name="personal")


class SyraBandModelTest(TestCase):
    """Tests for the SyraBand model."""

    def setUp(self):
        """Set up test data."""
        self.band_type = SyraBandType.objects.create(name="standard")
        self.band_use = SyraBandUse.objects.create(name="personal")

    def test_create_band(self):
        """Test creating a Syra Band."""
        band = SyraBand.objects.create(
            sku="BAND-001",
            name="Basic Syra Band",
            description="Entry level health band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=50,
            is_available=True,
        )
        self.assertEqual(band.name, "Basic Syra Band")
        self.assertEqual(band.sku, "BAND-001")
        self.assertEqual(band.price, Decimal("99.99"))
        self.assertEqual(band.stock_quantity, 50)

    def test_band_str_representation(self):
        """Test string representation of band."""
        band = SyraBand.objects.create(
            sku="BAND-002",
            name="Premium Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("199.99"),
            size="medium",
            color="black",
        )
        self.assertEqual(str(band), "Premium Band - medium - black")

    def test_unique_sku(self):
        """Test that SKU must be unique."""
        SyraBand.objects.create(
            sku="BAND-003",
            name="Band 1",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
        )
        with self.assertRaises(Exception):
            SyraBand.objects.create(
                sku="BAND-003",  # Same SKU
                name="Band 2",
                band_type=self.band_type,
                band_use=self.band_use,
                price=Decimal("99.99"),
            )

    def test_current_price_no_discount(self):
        """Test current_price returns regular price when no discount."""
        band = SyraBand.objects.create(
            sku="BAND-004",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
        )
        self.assertEqual(band.current_price, Decimal("100.00"))

    def test_current_price_with_discount(self):
        """Test current_price returns discount_price when available."""
        band = SyraBand.objects.create(
            sku="BAND-005",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
        )
        self.assertEqual(band.current_price, Decimal("80.00"))

    def test_has_discount_property(self):
        """Test has_discount property."""
        band_without_discount = SyraBand.objects.create(
            sku="BAND-006",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
        )
        self.assertFalse(band_without_discount.has_discount)

        band_with_discount = SyraBand.objects.create(
            sku="BAND-007",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            discount_price=Decimal("80.00"),
        )
        self.assertTrue(band_with_discount.has_discount)

    def test_discount_percentage(self):
        """Test discount_percentage calculation."""
        band = SyraBand.objects.create(
            sku="BAND-008",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            discount_price=Decimal("75.00"),
        )
        self.assertEqual(band.discount_percentage, 25)

    def test_discount_percentage_no_discount(self):
        """Test discount_percentage returns 0 when no discount."""
        band = SyraBand.objects.create(
            sku="BAND-009",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
        )
        self.assertEqual(band.discount_percentage, 0)

    def test_average_rating_no_reviews(self):
        """Test average_rating returns 0 when no reviews."""
        band = SyraBand.objects.create(
            sku="BAND-010",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
        )
        self.assertEqual(band.average_rating, 0)

    def test_review_count_no_reviews(self):
        """Test review_count returns 0 when no reviews."""
        band = SyraBand.objects.create(
            sku="BAND-011",
            name="Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
        )
        self.assertEqual(band.review_count, 0)

    def test_band_size_choices(self):
        """Test all band size choices."""
        sizes = ["small", "medium", "large", "xl"]
        for size in sizes:
            band = SyraBand.objects.create(
                sku=f"BAND-S{size}",
                name=f"Band {size}",
                band_type=self.band_type,
                band_use=self.band_use,
                price=Decimal("99.99"),
                size=size,
            )
            self.assertEqual(band.size, size)
            self.assertEqual(band.get_size_display(), dict(SyraBand.BAND_SIZES)[size])

    def test_band_color_choices(self):
        """Test all band color choices."""
        colors = ["black", "white", "blue", "red", "green"]
        for color in colors:
            band = SyraBand.objects.create(
                sku=f"BAND-C{color}",
                name=f"Band {color}",
                band_type=self.band_type,
                band_use=self.band_use,
                price=Decimal("99.99"),
                color=color,
            )
            self.assertEqual(band.color, color)

    def test_featured_band_ordering(self):
        """Test that featured bands appear first in ordering."""
        regular_band = SyraBand.objects.create(
            sku="BAND-REG",
            name="Regular Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            is_featured=False,
        )
        featured_band = SyraBand.objects.create(
            sku="BAND-FEAT",
            name="Featured Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("199.99"),
            is_featured=True,
        )
        bands = list(SyraBand.objects.all())
        self.assertEqual(bands[0], featured_band)
        self.assertEqual(bands[1], regular_band)


class OrderModelTest(TestCase):
    """Tests for the Order model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )

    def test_create_order(self):
        """Test creating an order."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
            tax_amount=Decimal("15.00"),
            total=Decimal("125.00"),
            shipping_name="John Doe",
            shipping_phone="01234567890",
            shipping_address="123 Main St",
            shipping_city="Cairo",
        )
        self.assertIsNotNone(order.order_number)
        self.assertTrue(order.order_number.startswith("SYRA-"))
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.payment_method, "cash")

    def test_order_str_representation(self):
        """Test string representation of order."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        self.assertEqual(str(order), f"Order #{order.order_number}")

    def test_order_number_unique(self):
        """Test that order numbers are unique."""
        order1 = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        # Create another user for second order
        user2 = SyraUser.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        order2 = Order.objects.create(
            user=user2,
            subtotal=Decimal("200.00"),
            total=Decimal("200.00"),
            shipping_name="Jane",
            shipping_phone="09876543210",
            shipping_address="456 St",
            shipping_city="Alexandria",
        )
        self.assertNotEqual(order1.order_number, order2.order_number)

    def test_order_total_calculation(self):
        """Test that total is calculated automatically."""
        order = Order(
            user=self.user,
            subtotal=Decimal("100.00"),
            shipping_cost=Decimal("10.00"),
            tax_amount=Decimal("15.00"),
            discount_amount=Decimal("5.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        order.save()
        self.assertEqual(order.total, Decimal("120.00"))

    def test_order_status_choices(self):
        """Test all order status choices."""
        statuses = [
            "pending",
            "processing",
            "shipped",
            "delivered",
            "cancelled",
            "refunded",
        ]
        for status in statuses:
            order = Order.objects.create(
                user=self.user,
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
                status=status,
                shipping_name="John",
                shipping_phone="01234567890",
                shipping_address="123 St",
                shipping_city="Cairo",
            )
            self.assertEqual(order.status, status)

    def test_payment_method_choices(self):
        """Test all payment method choices."""
        methods = ["cash", "card", "vodafone", "instapay", "bank"]
        for method in methods:
            order = Order.objects.create(
                user=self.user,
                subtotal=Decimal("100.00"),
                total=Decimal("100.00"),
                payment_method=method,
                shipping_name="John",
                shipping_phone="01234567890",
                shipping_address="123 St",
                shipping_city="Cairo",
            )
            self.assertEqual(order.payment_method, method)

    def test_get_tracking_url_aramex(self):
        """Test tracking URL generation for Aramex."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            tracking_number="123456789",
            carrier="aramex",
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        self.assertIn("aramex.com", order.get_tracking_url())

    def test_get_tracking_url_no_tracking(self):
        """Test tracking URL returns None when no tracking info."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        self.assertIsNone(order.get_tracking_url())


class OrderItemModelTest(TestCase):
    """Tests for the OrderItem model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.band_type = SyraBandType.objects.create(name="classic")
        self.band_use = SyraBandUse.objects.create(name="personal")
        self.product = SyraBand.objects.create(
            sku="BAND-001",
            name="Test Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            stock_quantity=50,
            size="medium",
        )
        self.order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )

    def test_create_order_item(self):
        """Test creating an order item."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("100.00"),
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.unit_price, Decimal("100.00"))
        self.assertEqual(item.total, Decimal("200.00"))
        self.assertEqual(item.product_name, "Test Band")
        self.assertEqual(item.product_sku, "BAND-001")

    def test_order_item_str_representation(self):
        """Test string representation of order item."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            unit_price=Decimal("50.00"),
        )
        self.assertEqual(str(item), "Test Band x 3")

    def test_order_item_total_with_discount(self):
        """Test order item total calculation with discount."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("100.00"),
            discount=Decimal("20.00"),
        )
        self.assertEqual(item.total, Decimal("180.00"))

    def test_order_item_snapshots_product_details(self):
        """Test that order item snapshots product details."""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        self.assertEqual(item.product_name, "Test Band")
        self.assertEqual(item.product_sku, "BAND-001")
        # Model uses get_size_display() and get_color_display() which returns human-readable values
        self.assertEqual(item.product_size, "Medium")
        self.assertEqual(item.product_color, "Black")


class CartModelTest(TestCase):
    """Tests for the Cart model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )

    def test_create_cart(self):
        """Test creating a cart."""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)

    def test_cart_str_representation(self):
        """Test string representation of cart."""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(str(cart), "Cart for testuser")

    def test_cart_total_items_empty(self):
        """Test total_items returns 0 for empty cart."""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.total_items, 0)

    def test_cart_total_price_empty(self):
        """Test total_price returns 0 for empty cart."""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.total_price, 0)

    def test_one_to_one_user(self):
        """Test that each user has only one cart."""
        Cart.objects.create(user=self.user)
        with self.assertRaises(Exception):
            Cart.objects.create(user=self.user)


class CartItemModelTest(TestCase):
    """Tests for the CartItem model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.band_type = SyraBandType.objects.create(name="standard")
        self.band_use = SyraBandUse.objects.create(name="personal")
        self.product = SyraBand.objects.create(
            sku="BAND-001",
            name="Test Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            stock_quantity=50,
        )
        self.cart = Cart.objects.create(user=self.user)

    def test_create_cart_item(self):
        """Test creating a cart item."""
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.total_price, Decimal("200.00"))

    def test_cart_item_str_representation(self):
        """Test string representation of cart item."""
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)
        self.assertEqual(str(item), "Test Band x 3")

    def test_cart_item_total_price(self):
        """Test total_price calculation."""
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=5)
        self.assertEqual(item.total_price, Decimal("500.00"))

    def test_cart_item_with_discount(self):
        """Test total_price with discount."""
        self.product.discount_price = Decimal("80.00")
        self.product.save()
        item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(item.total_price, Decimal("160.00"))

    def test_unique_cart_item(self):
        """Test unique constraint on cart item."""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
            size="medium",
            color="black",
        )
        with self.assertRaises(Exception):
            CartItem.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=2,
                size="medium",
                color="black",
            )

    def test_cart_total_items(self):
        """Test cart total_items with items."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        CartItem.objects.create(
            cart=self.cart, product=self.product, quantity=3, size="small", color="blue"
        )
        self.assertEqual(self.cart.total_items, 5)

    def test_cart_total_price(self):
        """Test cart total_price with items."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        self.assertEqual(self.cart.total_price, Decimal("200.00"))

    def test_cascade_delete_cart_item(self):
        """Test that cart items are deleted when cart is deleted."""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)
        self.assertEqual(CartItem.objects.count(), 1)
        self.cart.delete()
        self.assertEqual(CartItem.objects.count(), 0)


class BandReviewModelTest(TestCase):
    """Tests for the BandReview model."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.band_type = SyraBandType.objects.create(name="standard")
        self.band_use = SyraBandUse.objects.create(name="personal")
        self.product = SyraBand.objects.create(
            sku="BAND-001",
            name="Test Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            stock_quantity=50,
        )

    def test_create_review(self):
        """Test creating a review."""
        review = BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Great product!",
            comment="I love this band. It works perfectly.",
            verified_purchase=True,
            is_approved=True,
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.title, "Great product!")
        self.assertTrue(review.verified_purchase)
        self.assertTrue(review.is_approved)

    def test_review_str_representation(self):
        """Test string representation of review."""
        review = BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            title="Good product",
            comment="Nice band",
        )
        self.assertEqual(str(review), "Test Band - 4★ by testuser")

    def test_unique_user_review_per_product(self):
        """Test that user can only review a product once."""
        BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Great!",
            comment="First review",
        )
        with self.assertRaises(Exception):
            BandReview.objects.create(
                product=self.product,
                user=self.user,
                rating=3,
                title="Second review",
                comment="This shouldn't work",
            )

    def test_rating_validation_at_database_level(self):
        """Test rating accepts valid values."""
        # Rating validation is enforced at serializer level, not model level
        # Test that model accepts valid rating
        review = BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,  # Valid rating
            title="Valid rating",
            comment="Test",
        )
        self.assertEqual(review.rating, 5)

    def test_rating_range_behavior(self):
        """Test rating behavior."""
        # Model accepts any value; validation is at serializer level
        review = BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            title="Rating test",
            comment="Test",
        )
        self.assertEqual(review.rating, 3)

    def test_review_ordering(self):
        """Test that reviews are ordered by created_at descending."""
        review1 = BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            title="First",
            comment="First comment",
        )
        # Create another user for second review
        user2 = SyraUser.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        review2 = BandReview.objects.create(
            product=self.product,
            user=user2,
            rating=5,
            title="Second",
            comment="Second comment",
        )
        reviews = list(BandReview.objects.all())
        self.assertEqual(reviews[0], review2)  # Most recent first
        self.assertEqual(reviews[1], review1)

    def test_average_rating_with_reviews(self):
        """Test average_rating calculation with reviews."""
        user2 = SyraUser.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Great!",
            comment="5 stars",
        )
        BandReview.objects.create(
            product=self.product, user=user2, rating=3, title="OK", comment="3 stars"
        )
        self.assertEqual(self.product.average_rating, 4.0)

    def test_review_count_with_approved_reviews(self):
        """Test review_count only counts approved reviews."""
        user2 = SyraUser.objects.create_user(
            username="testuser2",
            email="test2@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        BandReview.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            title="Approved",
            comment="Approved review",
            is_approved=True,
        )
        BandReview.objects.create(
            product=self.product,
            user=user2,
            rating=3,
            title="Not Approved",
            comment="Not approved review",
            is_approved=False,
        )
        self.assertEqual(self.product.review_count, 1)  # Only approved


class OrderIntegrationTest(TestCase):
    """Integration tests for Order and OrderItem."""

    def setUp(self):
        """Set up test data."""
        self.user = SyraUser.objects.create_user(
            username="testuser",
            email="test@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        self.band_type = SyraBandType.objects.create(name="standard")
        self.band_use = SyraBandUse.objects.create(name="personal")
        self.band1 = SyraBand.objects.create(
            sku="BAND-001",
            name="Basic Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("100.00"),
            stock_quantity=50,
        )
        self.band2 = SyraBand.objects.create(
            sku="BAND-002",
            name="Premium Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("200.00"),
            stock_quantity=30,
        )

    def test_create_order_with_multiple_items(self):
        """Test creating an order with multiple items."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("300.00"),
            shipping_cost=Decimal("15.00"),
            tax_amount=Decimal("45.00"),
            total=Decimal("360.00"),
            shipping_name="John Doe",
            shipping_phone="01234567890",
            shipping_address="123 Main St",
            shipping_city="Cairo",
        )

        # Add items
        OrderItem.objects.create(
            order=order, product=self.band1, quantity=1, unit_price=Decimal("100.00")
        )
        OrderItem.objects.create(
            order=order, product=self.band2, quantity=1, unit_price=Decimal("200.00")
        )

        self.assertEqual(order.items.count(), 2)
        self.assertEqual(order.items.count(), 2)

    def test_order_items_cascade_delete(self):
        """Test that order items are deleted when order is deleted."""
        order = Order.objects.create(
            user=self.user,
            subtotal=Decimal("100.00"),
            total=Decimal("100.00"),
            shipping_name="John",
            shipping_phone="01234567890",
            shipping_address="123 St",
            shipping_city="Cairo",
        )
        OrderItem.objects.create(
            order=order, product=self.band1, quantity=1, unit_price=Decimal("100.00")
        )
        self.assertEqual(OrderItem.objects.count(), 1)
        order.delete()
        self.assertEqual(OrderItem.objects.count(), 0)


class BandTypeAPITest(TestCase):
    """Tests for the Band Type API endpoints."""

    def test_list_band_types(self):
        """Test listing band types."""
        SyraBandType.objects.create(name="classic", description="Classic band")
        response = self.client.get("/api/store/types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_band_type_authenticated(self):
        """Test creating band type with admin user."""
        # Create admin user with unique national_id
        user = SyraUser.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            national_id="99999999999999",
            password="adminpass123",
        )
        # Get JWT token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "99999999999999", "password": "adminpass123"},
        )
        token = response.data["access"]
        data = {"name": "premium", "description": "Premium band"}
        response = self.client.post(
            "/api/store/types/", data, HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class BandAPITest(TestCase):
    """Tests for the Band API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.band_type = SyraBandType.objects.create(name="standard")
        self.band_use = SyraBandUse.objects.create(name="personal")

    def test_list_bands(self):
        """Test listing bands."""
        SyraBand.objects.create(
            sku="TEST-001",
            name="Test Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
        )
        response = self.client.get("/api/store/bands/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_list_available_bands_only(self):
        """Test that only available bands are listed."""
        # Available band
        SyraBand.objects.create(
            sku="TEST-001",
            name="Available Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
            is_available=True,
        )
        # Unavailable band
        SyraBand.objects.create(
            sku="TEST-002",
            name="Unavailable Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=0,
            is_available=False,
        )
        # Use available_only query param to filter
        response = self.client.get("/api/store/bands/?available_only=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see available band
        self.assertEqual(len(response.data["results"]), 1)

    def test_band_detail(self):
        """Test getting band detail."""
        band = SyraBand.objects.create(
            sku="TEST-001",
            name="Test Band",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
        )
        response = self.client.get(f"/api/store/bands/{band.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Band")


class OrderAPITest(TestCase):
    """Tests for the Order API endpoints."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="ordertest",
            email="order@example.com",
            national_id="12345678901234",
            password="testpass123",
        )
        # Get token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "12345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_list_orders_authenticated(self):
        """Test listing orders with authentication."""
        response = self.client.get(
            "/api/store/orders/", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_orders_unauthenticated(self):
        """Test listing orders without authentication."""
        response = self.client.get("/api/store/orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_order(self):
        """Test creating an order."""
        # First create a band
        band_type = SyraBandType.objects.create(name="standard")
        band_use = SyraBandUse.objects.create(name="personal")
        band = SyraBand.objects.create(
            sku="TEST-001",
            name="Test Band",
            band_type=band_type,
            band_use=band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
        )

        # Use explicit JSON content
        import json

        json_data = json.dumps(
            {
                "items": [{"product_id": band.id, "quantity": 1}],
                "payment_method": "cash",
                "shipping_name": "Test User",
                "shipping_phone": "01234567890",
                "shipping_address": "123 Test St",
                "shipping_city": "Cairo",
            }
        )
        response = self.client.post(
            "/api/store/orders/",
            data=json_data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Order error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class CartAPITest(TestCase):
    """Tests for the Cart API endpoints."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="carttest",
            email="cart@example.com",
            national_id="22345678901234",
            password="testpass123",
        )
        # Get token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "22345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_get_cart_authenticated(self):
        """Test getting cart with authentication."""
        response = self.client.get(
            "/api/store/cart/", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_cart_unauthenticated(self):
        """Test getting cart without authentication."""
        response = self.client.get("/api/store/cart/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_add_to_cart(self):
        """Test adding item to cart."""
        # First create a band
        band_type = SyraBandType.objects.create(name="standard2")
        band_use = SyraBandUse.objects.create(name="personal2")
        band = SyraBand.objects.create(
            sku="TEST-002",
            name="Test Band 2",
            band_type=band_type,
            band_use=band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
        )

        data = {"product_id": band.id, "quantity": 2}
        response = self.client.post(
            "/api/store/cart/add_item/", data, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        # Returns 200 - the view returns the cart after adding
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_items"], 2)


class BandRegistrationAPITest(TestCase):
    """Tests for the Band Registration API endpoints."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="regtest",
            email="reg@example.com",
            national_id="32345678901234",
            password="testpass123",
        )
        # Get token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "32345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

    def test_list_registrations_authenticated(self):
        """Test listing band registrations."""
        response = self.client.get(
            "/api/store/registrations/", HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BandReviewAPITest(TestCase):
    """Tests for the Band Review API endpoints."""

    def setUp(self):
        """Set up test user."""
        self.user = SyraUser.objects.create_user(
            username="reviewtest",
            email="review@example.com",
            national_id="42345678901234",
            password="testpass123",
        )
        # Get token
        response = self.client.post(
            "/api/accounts/login/",
            {"national_id": "42345678901234", "password": "testpass123"},
        )
        self.token = response.data["access"]

        # Create band
        self.band_type = SyraBandType.objects.create(name="standard3")
        self.band_use = SyraBandUse.objects.create(name="personal3")
        self.band = SyraBand.objects.create(
            sku="TEST-003",
            name="Test Band 3",
            band_type=self.band_type,
            band_use=self.band_use,
            price=Decimal("99.99"),
            stock_quantity=10,
        )

    def test_create_review(self):
        """Test creating a review."""
        data = {
            "product": self.band.id,
            "rating": 5,
            "title": "Great product!",
            "comment": "Great product!",
        }
        response = self.client.post(
            "/api/store/reviews/", data, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Review error: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["rating"], 5)

    def test_list_reviews(self):
        """Test listing reviews."""
        BandReview.objects.create(
            product=self.band, user=self.user, rating=4, comment="Good"
        )
        response = self.client.get(f"/api/store/bands/{self.band.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
