"""
Store Analytics - Dashboard views for sales reports, stock alerts, and revenue tracking.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, F
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from datetime import timedelta
from store.models import Order, OrderItem, SyraBand, BandRegistration


def is_store_admin(user):
    """Check if user is a store admin."""
    return (
        user.is_staff
        or hasattr(user, "store_role")
        and user.store_role in ["store_admin", "product_manager", "price_manager"]
    )


@login_required
@user_passes_test(is_store_admin)
def analytics_dashboard(request):
    """Main analytics dashboard."""
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # Get date range from request (with max limit to prevent DoS)
    try:
        days = min(int(request.GET.get("days", 30)), 365)
        days = max(days, 1)  # Ensure at least 1 day
    except (ValueError, TypeError):
        days = 30
    start_date = today - timedelta(days=days)

    # Revenue metrics
    total_revenue = (
        Order.objects.filter(
            status__in=["processing", "shipped", "delivered"],
            created_at__date__gte=start_date,
        ).aggregate(total=Sum("total"))["total"]
        or 0
    )

    orders_count = Order.objects.filter(created_at__date__gte=start_date).count()

    # Average order value
    avg_order_value = total_revenue / orders_count if orders_count > 0 else 0

    # Today's stats
    today_orders = Order.objects.filter(created_at__date=today)
    today_revenue = today_orders.aggregate(total=Sum("total"))["total"] or 0

    # Orders by status
    orders_by_status = (
        Order.objects.annotate(status_count=Count("id"))
        .values("status")
        .annotate(count=Count("id"))
    )

    # Top selling products
    top_products = (
        OrderItem.objects.filter(order__created_at__date__gte=start_date)
        .values("product__name", "product__sku")
        .annotate(total_sold=Sum("quantity"), revenue=Sum("total"))
        .order_by("-total_sold")[:10]
    )

    # Low stock alerts
    low_stock_products = SyraBand.objects.filter(
        stock_quantity__lt=10, is_active=True
    ).order_by("stock_quantity")[:10]

    out_of_stock_products = SyraBand.objects.filter(stock_quantity=0, is_active=True)

    # Orders over time (daily)
    daily_orders = (
        Order.objects.filter(created_at__date__gte=start_date)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(count=Count("id"), revenue=Sum("total"))
        .order_by("day")
    )

    # Band registrations
    total_registrations = BandRegistration.objects.count()
    active_registrations = BandRegistration.objects.filter(status="active").count()

    # Sales by product type
    sales_by_type = (
        OrderItem.objects.filter(order__created_at__date__gte=start_date)
        .values("product__band_type__name")
        .annotate(count=Sum("quantity"), revenue=Sum("total"))
        .order_by("-count")
    )

    # Recent orders
    recent_orders = Order.objects.select_related("user").order_by("-created_at")[:10]

    context = {
        "total_revenue": total_revenue,
        "orders_count": orders_count,
        "avg_order_value": avg_order_value,
        "today_revenue": today_revenue,
        "today_orders_count": today_orders.count(),
        "orders_by_status": orders_by_status,
        "top_products": top_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "daily_orders": daily_orders,
        "total_registrations": total_registrations,
        "active_registrations": active_registrations,
        "sales_by_type": sales_by_type,
        "recent_orders": recent_orders,
        "days": days,
    }

    return render(request, "store/analytics.html", context)


@login_required
@user_passes_test(is_store_admin)
def sales_report(request):
    """Detailed sales report."""
    # Monthly sales
    monthly_sales = (
        Order.objects.filter(status__in=["processing", "shipped", "delivered"])
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(orders=Count("id"), revenue=Sum("total"), avg_order=Avg("total"))
        .order_by("-month")[:12]
    )

    # Products performance
    products_performance = (
        OrderItem.objects.filter(
            order__status__in=["processing", "shipped", "delivered"]
        )
        .values("product__name", "product__sku", "product__price")
        .annotate(
            units_sold=Sum("quantity"),
            total_revenue=Sum("total"),
            orders=Count("order", distinct=True),
        )
        .order_by("-total_revenue")[:20]
    )

    context = {
        "monthly_sales": monthly_sales,
        "products_performance": products_performance,
    }

    return render(request, "store/sales_report.html", context)
