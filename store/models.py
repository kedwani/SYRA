"""
Models for the Syra Store app.
Includes Syra Band products with different types and uses, orders, and order items.
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class SyraBandType(models.Model):
    """
    Types of Syra Band available (Standard, Premium, Kids, Senior, Sport).
    """

    BAND_TYPES = [
        ("standard", "Standard"),
        ("premium", "Premium"),
        ("kids", "Kids"),
        ("senior", "Senior"),
        ("sport", "Sport"),
        ("medical", "Medical"),
    ]

    name = models.CharField(max_length=20, choices=BAND_TYPES, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Syra Band Type"
        verbose_name_plural = "Syra Band Types"

    def __str__(self):
        return self.get_name_display()


class SyraBandUse(models.Model):
    """
    Different use cases/purposes for Syra Band.
    """

    USE_CASES = [
        ("personal", "Personal Health"),
        ("child", "Child Safety"),
        ("elderly", "Elderly Care"),
        ("athlete", "Athlete Monitoring"),
        ("patient", "Patient Monitoring"),
        ("employee", "Employee Health"),
        ("traveler", "Traveler Safety"),
    ]

    name = models.CharField(max_length=20, choices=USE_CASES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or name")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Syra Band Use"
        verbose_name_plural = "Syra Band Uses"

    def __str__(self):
        return self.get_name_display()


class SyraBand(models.Model):
    """
    Main product model for Syra Band with different variations.
    """

    BAND_SIZES = [
        ("small", "Small (For Kids)"),
        ("medium", "Medium (Standard)"),
        ("large", "Large"),
        ("xl", "Extra Large"),
    ]

    BAND_COLORS = [
        ("black", "Black"),
        ("white", "White"),
        ("blue", "Blue"),
        ("red", "Red"),
        ("green", "Green"),
        ("pink", "Pink"),
        ("orange", "Orange"),
        ("purple", "Purple"),
    ]

    BAND_MATERIALS = [
        ("silicone", "Silicone"),
        ("leather", "Leather"),
        ("fabric", "Fabric"),
        ("metal", "Metal"),
        ("hybrid", "Hybrid"),
    ]

    # Product identification
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=200, blank=True)

    # Band characteristics
    band_type = models.ForeignKey(
        SyraBandType, on_delete=models.PROTECT, related_name="products"
    )
    band_use = models.ForeignKey(
        SyraBandUse, on_delete=models.PROTECT, related_name="products"
    )
    size = models.CharField(max_length=20, choices=BAND_SIZES, default="medium")
    color = models.CharField(max_length=20, choices=BAND_COLORS, default="black")
    material = models.CharField(
        max_length=20, choices=BAND_MATERIALS, default="silicone"
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )

    # Stock management
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    allow_preorder = models.BooleanField(default=False)

    # Features
    has_nfc = models.BooleanField(default=True, help_text="NFC chip included")
    has_qr_code = models.BooleanField(default=True, help_text="QR code included")
    has_gps = models.BooleanField(default=False, help_text="GPS tracking included")
    has_heart_rate = models.BooleanField(default=False, help_text="Heart rate monitor")
    has_water_resistant = models.BooleanField(default=True, help_text="Water resistant")
    battery_life = models.CharField(max_length=50, blank=True, help_text="e.g., 7 days")

    # Images
    image = models.ImageField(upload_to="store/band_images/", blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="store/band_thumbnails/", blank=True, null=True
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Syra Band"
        verbose_name_plural = "Syra Bands"
        ordering = ["-is_featured", "-created_at"]

    def __str__(self):
        return f"{self.name} - {self.size} - {self.color}"

    @property
    def current_price(self):
        """Get the current price (discounted if available)."""
        return self.discount_price if self.discount_price else self.price

    @property
    def has_discount(self):
        """Check if the product has a discount."""
        return self.discount_price is not None and self.discount_price < self.price

    @property
    def discount_percentage(self):
        """Calculate discount percentage."""
        from decimal import Decimal

        if self.has_discount:
            discount = Decimal(1) - (self.discount_price / self.price)
            return int(discount * Decimal(100))
        return 0


class Order(models.Model):
    """
    Order model for storing purchase information.
    """

    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHODS = [
        ("cash", "Cash on Delivery"),
        ("card", "Credit/Debit Card"),
        ("vodafone", "Vodafone Cash"),
        ("instapay", "InstaPay"),
        ("bank", "Bank Transfer"),
    ]

    # Order identification
    order_number = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default="cash"
    )
    payment_status = models.BooleanField(default=False)

    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping information
    shipping_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=15)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_area = models.CharField(max_length=100, blank=True)
    shipping_notes = models.TextField(blank=True)

    # Notes
    user_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"SYRA-{uuid.uuid4().hex[:8].upper()}"
        if not self.total:
            self.total = (
                self.subtotal
                + self.shipping_cost
                + self.tax_amount
                - self.discount_amount
            )
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """
    Individual items in an order.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        SyraBand, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Product details snapshot (in case product is modified later)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    product_size = models.CharField(max_length=20)
    product_color = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        if not self.product_size:
            self.product_size = self.product.get_size_display()
        if not self.product_color:
            self.product_color = self.product.get_color_display()
        if not self.unit_price:
            self.unit_price = self.product.current_price

        self.total = (self.unit_price * self.quantity) - self.discount
        super().save(*args, **kwargs)


class Cart(models.Model):
    """
    Shopping cart for users.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Items in the shopping cart.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        SyraBand, on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    size = models.CharField(max_length=20, default="medium")
    color = models.CharField(max_length=20, default="black")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ["cart", "product", "size", "color"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.current_price * self.quantity


class BandRegistration(models.Model):
    """
    Links a purchased Syra Band to a user's medical profile.
    """

    BAND_STATUS = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("lost", "Lost"),
        ("damaged", "Damaged"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="band_registrations",
    )
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="registrations"
    )
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nickname = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=BAND_STATUS, default="active")
    activated_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Band Registration"
        verbose_name_plural = "Band Registrations"

    def __str__(self):
        return f"{self.nickname or self.public_id} - {self.user.username}"
