"""
Template views for the Syra Store frontend.
"""

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F

from .models import (
    SyraBand,
    SyraBandType,
    SyraBandUse,
    Cart,
    CartItem,
    Order,
    BandRegistration,
    SavedAddress,
)


def store_home(request):
    """Home page for the Syra Store."""
    # Get featured products
    featured_bands = SyraBand.objects.filter(
        is_active=True, is_featured=True, stock_quantity__gt=0
    )[:6]

    # Get all band types and uses for filtering
    band_types = SyraBandType.objects.filter(is_active=True)
    band_uses = SyraBandUse.objects.filter(is_active=True)

    # Get latest products
    latest_bands = SyraBand.objects.filter(
        is_active=True, stock_quantity__gt=0
    ).order_by("-created_at")[:8]

    context = {
        "featured_bands": featured_bands,
        "band_types": band_types,
        "band_uses": band_uses,
        "latest_bands": latest_bands,
    }
    return render(request, "store/home.html", context)


def band_list(request):
    """List all available Syra Bands with filtering."""
    bands = SyraBand.objects.filter(is_active=True, stock_quantity__gt=0)

    # Filter by type
    band_type = request.GET.get("type")
    if band_type:
        bands = bands.filter(band_type__name=band_type)

    # Filter by use
    band_use = request.GET.get("use")
    if band_use:
        bands = bands.filter(band_use__name=band_use)

    # Filter by size
    size = request.GET.get("size")
    if size:
        bands = bands.filter(size=size)

    # Filter by color
    color = request.GET.get("color")
    if color:
        bands = bands.filter(color=color)

    # Filter by material
    material = request.GET.get("material")
    if material:
        bands = bands.filter(material=material)

    # Filter by price range
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        bands = bands.filter(price__gte=min_price)
    if max_price:
        bands = bands.filter(price__lte=max_price)

    # Filter by features
    has_nfc = request.GET.get("has_nfc")
    if has_nfc:
        bands = bands.filter(has_nfc=True)

    has_gps = request.GET.get("has_gps")
    if has_gps:
        bands = bands.filter(has_gps=True)

    has_heart_rate = request.GET.get("has_heart_rate")
    if has_heart_rate:
        bands = bands.filter(has_heart_rate=True)

    # Pagination
    paginator = Paginator(bands, 12)
    page = request.GET.get("page")
    try:
        bands = paginator.page(page)
    except PageNotAnInteger:
        bands = paginator.page(1)
    except EmptyPage:
        bands = paginator.page(paginator.num_pages)

    # Get filter options
    band_types = SyraBandType.objects.filter(is_active=True)
    band_uses = SyraBandUse.objects.filter(is_active=True)

    context = {
        "bands": bands,
        "band_types": band_types,
        "band_uses": band_uses,
        "current_filters": {
            "type": band_type,
            "use": band_use,
            "size": size,
            "color": color,
            "material": material,
            "min_price": min_price,
            "max_price": max_price,
        },
    }
    return render(request, "store/band_list.html", context)


def band_detail(request, band_id):
    """Detailed view of a Syra Band product."""
    band = get_object_or_404(SyraBand, id=band_id, is_active=True)

    # Get related products (same type or use)
    related_bands = (
        SyraBand.objects.filter(is_active=True, stock_quantity__gt=0)
        .filter(band_type=band.band_type)
        .exclude(id=band.id)[:4]
    )

    context = {
        "band": band,
        "related_bands": related_bands,
    }
    return render(request, "store/band_detail.html", context)


@login_required
def cart_view(request):
    """View the shopping cart."""
    from django.conf import settings
    from decimal import Decimal

    cart = Cart.objects.prefetch_related("items", "items__product").get_or_create(
        user=request.user
    )[0]

    # Calculate order summary values (consistent with checkout)
    subtotal = cart.total_price
    shipping_cost = Decimal(str(settings.STORE_SHIPPING_COST))
    tax_rate = Decimal(str(settings.STORE_TAX_RATE))
    tax_amount = (subtotal + shipping_cost) * tax_rate
    total = subtotal + shipping_cost + tax_amount

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax_amount": tax_amount,
        "total": total,
    }
    return render(request, "store/cart.html", context)


@login_required
@csrf_protect
def add_to_cart(request, band_id):
    """Add a product to the cart."""
    if request.method == "POST":
        band = get_object_or_404(SyraBand, id=band_id, is_active=True)
        quantity = int(request.POST.get("quantity", 1))
        size = request.POST.get("size", "medium")
        color = request.POST.get("color", "black")

        if band.stock_quantity < quantity:
            messages.error(request, "Sorry, the requested quantity is not available.")
            return redirect("store:band_detail", band_id=band_id)

        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if item already exists
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=band,
            size=size,
            color=color,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > 10:
                cart_item.quantity = 10
            cart_item.save()

        messages.success(request, f"{band.name} added to your cart!")
        return redirect("store:cart")

    return redirect("store:band_list")


@login_required
@csrf_protect
def update_cart_item(request, item_id):
    """Update cart item quantity."""
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)
        quantity = int(request.POST.get("quantity", 1))

        try:
            cart_item = CartItem.objects.select_related("product").get(
                id=item_id, cart=cart
            )

            # Verify ownership - ensure cart_item belongs to this user's cart
            if cart_item.cart.user != request.user:
                messages.error(request, "Item not found in cart.")
                return redirect("store:cart")

            if quantity <= 0:
                cart_item.delete()
                messages.success(request, "Item removed from cart.")
            else:
                # Validate stock availability before updating
                if quantity > cart_item.product.stock_quantity:
                    messages.error(
                        request,
                        f"Sorry, only {cart_item.product.stock_quantity} items available in stock.",
                    )
                    return redirect("store:cart")

                cart_item.quantity = min(quantity, 10)
                cart_item.save()
                messages.success(request, "Cart updated.")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in cart.")

    return redirect("store:cart")


@login_required
@csrf_protect
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    if request.method == "POST":
        cart, _ = Cart.objects.get_or_create(user=request.user)

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)

            # Verify ownership - ensure cart_item belongs to this user's cart
            if cart_item.cart.user != request.user:
                messages.error(request, "Item not found in cart.")
                return redirect("store:cart")

            cart_item.delete()
            messages.success(request, "Item removed from cart.")
        except CartItem.DoesNotExist:
            messages.error(request, "Item not found in cart.")

    return redirect("store:cart")


@login_required
@transaction.atomic
@csrf_protect
def checkout(request):
    """Checkout process."""
    cart, _ = Cart.objects.select_for_update().get_or_create(user=request.user)

    if not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("store:band_list")

    if request.method == "POST":
        import logging

        logger = logging.getLogger(__name__)

        # Calculate totals (use Decimal for precision)
        from django.conf import settings

        subtotal = cart.total_price
        shipping_cost = Decimal(str(settings.STORE_SHIPPING_COST))
        tax_rate = Decimal(str(settings.STORE_TAX_RATE))
        tax_amount = (subtotal + shipping_cost) * tax_rate
        total = subtotal + shipping_cost + tax_amount

        # Check stock availability first
        for item in cart.items.select_for_update():
            product = item.product
            if product.stock_quantity < item.quantity:
                messages.error(
                    request,
                    f"{product.name} is out of stock. Only {product.stock_quantity} available.",
                )
                return redirect("store:cart")

        # Create order
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total=total,
            payment_method=request.POST.get("payment_method", "cash"),
            shipping_name=request.POST.get("shipping_name"),
            shipping_phone=request.POST.get("shipping_phone"),
            shipping_address=request.POST.get("shipping_address"),
            shipping_city=request.POST.get("shipping_city"),
            shipping_area=request.POST.get("shipping_area", ""),
            shipping_notes=request.POST.get("shipping_notes", ""),
            user_notes=request.POST.get("user_notes", ""),
        )

        # Create order items and update stock atomically
        for item in cart.items.select_for_update():
            from .models import OrderItem

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.current_price,
                total=item.total_price,
            )

            # Atomic stock update
            SyraBand.objects.filter(id=item.product.id).update(
                stock_quantity=F("stock_quantity") - item.quantity
            )

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect("store:order_detail", order_id=order.id)

    # Calculate totals for display
    from django.conf import settings

    subtotal = cart.total_price
    shipping_cost = Decimal(str(settings.STORE_SHIPPING_COST))
    tax_rate = Decimal(str(settings.STORE_TAX_RATE))
    tax_amount = subtotal * tax_rate
    total = subtotal + shipping_cost + tax_amount

    context = {
        "cart": cart,
        "subtotal": subtotal,
        "shipping_cost": shipping_cost,
        "tax_amount": tax_amount,
        "total": total,
    }
    return render(request, "store/checkout.html", context)


@login_required
def order_list(request):
    """List user's orders."""
    orders = (
        Order.objects.select_related("user")
        .prefetch_related("items", "items__product")
        .filter(user=request.user)
        .order_by("-created_at")
    )

    context = {
        "orders": orders,
    }
    return render(request, "store/order_list.html", context)


@login_required
def order_detail(request, order_id):
    """View order details."""
    order = get_object_or_404(
        Order.objects.select_related("user").prefetch_related(
            "items", "items__product"
        ),
        id=order_id,
        user=request.user,
    )

    context = {
        "order": order,
    }
    return render(request, "store/order_detail.html", context)


@login_required
def my_bands(request):
    """View user's registered Syra Bands."""
    registrations = (
        BandRegistration.objects.select_related("user", "order_item", "medical_profile")
        .filter(user=request.user)
        .order_by("-created_at")
    )

    context = {
        "registrations": registrations,
    }
    return render(request, "store/my_bands.html", context)


def get_cart_count(request):
    """API endpoint to get cart item count."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return JsonResponse({"count": cart.total_items})
    return JsonResponse({"count": 0})


def filter_bands(request):
    """AJAX endpoint to filter bands."""
    bands = SyraBand.objects.filter(is_active=True, stock_quantity__gt=0)

    # Apply filters
    band_type = request.GET.get("type")
    band_use = request.GET.get("use")
    size = request.GET.get("size")
    color = request.GET.get("color")
    material = request.GET.get("material")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if band_type:
        bands = bands.filter(band_type__name=band_type)
    if band_use:
        bands = bands.filter(band_use__name=band_use)
    if size:
        bands = bands.filter(size=size)
    if color:
        bands = bands.filter(color=color)
    if material:
        bands = bands.filter(material=material)
    if min_price:
        bands = bands.filter(price__gte=min_price)
    if max_price:
        bands = bands.filter(price__lte=max_price)

    # Serialize data
    data = [
        {
            "id": band.id,
            "name": band.name,
            "price": str(band.price),
            "discount_price": str(band.discount_price) if band.discount_price else None,
            "current_price": str(band.current_price),
            "has_discount": band.has_discount,
            "discount_percentage": band.discount_percentage,
            "size": band.size,
            "color": band.color,
            "material": band.material,
            "has_nfc": band.has_nfc,
            "has_gps": band.has_gps,
            "has_heart_rate": band.has_heart_rate,
            "thumbnail": band.thumbnail.url if band.thumbnail else None,
        }
        for band in bands
    ]

    return JsonResponse({"bands": data})


@login_required
def order_cancel(request, order_id):
    """Cancel an order."""
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status not in ["pending", "processing"]:
            messages.error(request, "Order cannot be cancelled in current status.")
            return redirect("store:order_detail", order_id=order_id)

        # Restore stock atomically
        for item in order.items.select_related("product").all():
            SyraBand.objects.filter(id=item.product.id).update(
                stock_quantity=F("stock_quantity") + item.quantity
            )

        order.status = "cancelled"
        order.save()

        messages.success(request, f"Order #{order.order_number} has been cancelled.")

    return redirect("store:order_list")


@login_required
def registration_activate(request, reg_id):
    """Activate a band registration."""
    if request.method == "POST":
        from django.utils import timezone
        from datetime import timedelta

        registration = get_object_or_404(BandRegistration, id=reg_id, user=request.user)
        registration.status = "active"
        registration.activated_at = timezone.now().date()
        registration.expires_at = registration.activated_at + timedelta(days=365)
        registration.save()

        messages.success(request, "Band activated successfully!")

    return redirect("store:my_bands")


@login_required
def registration_report_lost(request, reg_id):
    """Report a band as lost."""
    if request.method == "POST":
        registration = get_object_or_404(BandRegistration, id=reg_id, user=request.user)
        registration.status = "lost"
        registration.save()

        messages.success(request, "Band reported as lost.")

    return redirect("store:my_bands")


@login_required
def registration_update_nickname(request, reg_id):
    """Update band nickname."""
    if request.method == "POST":
        registration = get_object_or_404(BandRegistration, id=reg_id, user=request.user)
        registration.nickname = request.POST.get("nickname", "")
        registration.save()

        messages.success(request, "Band nickname updated!")

    return redirect("store:my_bands")


@login_required
def addresses_view(request):
    """View and manage saved addresses."""
    addresses = SavedAddress.objects.filter(user=request.user)

    # Also get addresses from previous orders
    order_addresses = (
        Order.objects.filter(user=request.user)
        .values(
            "shipping_name",
            "shipping_phone",
            "shipping_address",
            "shipping_city",
            "shipping_area",
        )
        .distinct()
    )

    if request.method == "POST":
        # Add new address
        label = request.POST.get("label", "")
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        area = request.POST.get("area", "")
        notes = request.POST.get("notes", "")
        is_default = request.POST.get("is_default", False) == "on"

        if is_default:
            # Unset other default addresses
            SavedAddress.objects.filter(user=request.user, is_default=True).update(
                is_default=False
            )

        SavedAddress.objects.create(
            user=request.user,
            label=label,
            name=name,
            phone=phone,
            address=address,
            city=city,
            area=area,
            notes=notes,
            is_default=is_default,
        )
        messages.success(request, "Address saved successfully!")
        return redirect("store:addresses")

    context = {
        "addresses": addresses,
        "order_addresses": order_addresses,
    }
    return render(request, "store/addresses.html", context)


@login_required
@csrf_protect
def address_delete(request, address_id):
    """Delete a saved address."""
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted!")
    return redirect("store:addresses")


@login_required
@csrf_protect
def address_set_default(request, address_id):
    """Set an address as default."""
    # Unset all defaults
    SavedAddress.objects.filter(user=request.user, is_default=True).update(
        is_default=False
    )

    # Set new default
    address = get_object_or_404(SavedAddress, id=address_id, user=request.user)
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated!")
    return redirect("store:addresses")
