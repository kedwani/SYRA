"""
Store models for SYRA.
Manages products and orders for the e-commerce section.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    """
    Product model for e-commerce (bracelets, accessories).
    """
    
    # Product type
    TYPE_BRACELET = 'bracelet'
    TYPE_ACCESSORY = 'accessory'
    TYPE_BUNDLE = 'bundle'
    
    TYPE_CHOICES = [
        (TYPE_BRACELET, 'Bracelet'),
        (TYPE_ACCESSORY, 'Accessory'),
        (TYPE_BUNDLE, 'Bundle'),
    ]
    
    # Status
    STATUS_ACTIVE = 'active'
    STATUS_INACTIVE = 'inactive'
    STATUS_OUT_OF_STOCK = 'out_of_stock'
    
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_OUT_OF_STOCK, 'Out of Stock'),
    ]
    
    # UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic info
    name = models.CharField(max_length=200, verbose_name=_('product name'))
    slug = models.SlugField(max_length=220, unique=True, verbose_name=_('slug'))
    description = models.TextField(verbose_name=_('description'))
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('short description')
    )
    
    # Type and category
    product_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_BRACELET,
        verbose_name=_('product type')
    )
    category = models.CharField(max_length=100, blank=True, verbose_name=_('category'))
    
    # Pricing (stored in cents for precision)
    price = models.PositiveIntegerField(verbose_name=_('price in cents'))
    compare_at_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('compare at price')
    )
    cost_per_item = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('cost per item')
    )
    
    # Inventory
    sku = models.CharField(max_length=100, unique=True, verbose_name=_('SKU'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('quantity'))
    track_inventory = models.BooleanField(default=True, verbose_name=_('track inventory'))
    allow_oversell = models.BooleanField(default=False, verbose_name=_('allow oversell'))
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        verbose_name=_('status')
    )
    
    # Images
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        verbose_name=_('main image')
    )
    images = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('additional images')
    )
    
    # Metadata
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_('Weight in grams'),
        verbose_name=_('weight (g)')
    )
    is_featured = models.BooleanField(default=False, verbose_name=_('is featured'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def price_formatted(self):
        """Return formatted price."""
        return f"${self.price / 100:.2f}"
    
    @property
    def compare_at_price_formatted(self):
        """Return formatted compare at price."""
        if self.compare_at_price:
            return f"${self.compare_at_price / 100:.2f}"
        return None
    
    @property
    def in_stock(self):
        """Check if product is in stock."""
        return self.quantity > 0 if self.track_inventory else True


class Order(models.Model):
    """
    Order model for tracking purchases.
    """
    
    # Status
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SHIPPED, 'Shipped'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REFUNDED, 'Refunded'),
    ]
    
    # Payment method
    PAYMENT_CASH = 'cash'
    PAYMENT_CARD = 'card'
    PAYMENT_WALLET = 'wallet'
    
    PAYMENT_CHOICES = [
        (PAYMENT_CASH, 'Cash on Delivery'),
        (PAYMENT_CARD, 'Card Payment'),
        (PAYMENT_WALLET, 'Digital Wallet'),
    ]
    
    # UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('user')
    )
    
    # Contact info
    customer_email = models.EmailField(verbose_name=_('customer email'))
    customer_phone = models.CharField(max_length=20, verbose_name=_('customer phone'))
    
    # Shipping address
    shipping_name = models.CharField(max_length=200, verbose_name=_('shipping name'))
    shipping_address = models.TextField(verbose_name=_('shipping address'))
    shipping_city = models.CharField(max_length=100, verbose_name=_('shipping city'))
    shipping_postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('postal code'))
    shipping_country = models.CharField(
        max_length=50,
        default='Egypt',
        verbose_name=_('country')
    )
    
    # Order totals (stored in cents)
    subtotal = models.PositiveIntegerField(verbose_name=_('subtotal'))
    shipping_cost = models.PositiveIntegerField(
        default=0,
        verbose_name=_('shipping cost')
    )
    tax = models.PositiveIntegerField(default=0, verbose_name=_('tax'))
    total = models.PositiveIntegerField(verbose_name=_('total'))
    
    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default=PAYMENT_CASH,
        verbose_name=_('payment method')
    )
    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_('payment status')
    )
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_('transaction ID'))
    
    # Order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name=_('status')
    )
    
    # Notes
    notes = models.TextField(blank=True, verbose_name=_('notes'))
    internal_notes = models.TextField(blank=True, verbose_name=_('internal notes'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name=_('paid at'))
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name=_('shipped at'))
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name=_('delivered at'))
    
    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id.hex[:8].upper()}"
    
    @property
    def total_formatted(self):
        """Return formatted total."""
        return f"${self.total / 100:.2f}"


class OrderItem(models.Model):
    """
    Individual items in an order.
    """
    
    # UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Order relationship
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('order')
    )
    
    # Product
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('product')
    )
    
    # Item details
    name = models.CharField(max_length=200, verbose_name=_('product name'))
    sku = models.CharField(max_length=100, blank=True, verbose_name=_('SKU'))
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    price = models.PositiveIntegerField(verbose_name=_('price per unit'))
    total = models.PositiveIntegerField(verbose_name=_('total'))
    
    # Bracelet linking (if applicable)
    bracelet = models.ForeignKey(
        'hardware.Bracelet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name=_('bracelet')
    )
    
    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')
    
    def __str__(self):
        return f"{self.name} x{self.quantity}"
    
    @property
    def price_formatted(self):
        """Return formatted price."""
        return f"${self.price / 100:.2f}"
    
    @property
    def total_formatted(self):
        """Return formatted total."""
        return f"${self.total / 100:.2f}"