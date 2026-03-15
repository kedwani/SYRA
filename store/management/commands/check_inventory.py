"""
Management command to check inventory levels and alert for low stock items.
Run with: python manage.py check_inventory
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from store.models import SyraBand


class Command(BaseCommand):
    help = "Check inventory levels and alert for low stock items"

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold",
            type=int,
            default=10,
            help="Stock quantity threshold for low stock alert (default: 10)",
        )
        parser.add_argument(
            "--email", action="store_true", help="Send email alerts to admins"
        )

    def handle(self, *args, **options):
        threshold = options["threshold"]
        send_email = options["email"]

        low_stock_products = SyraBand.objects.filter(
            stock_quantity__lte=threshold, is_active=True
        ).order_by("stock_quantity")

        if not low_stock_products.exists():
            self.stdout.write(
                self.style.SUCCESS("All products have sufficient stock levels.")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"\n=== Low Stock Alert: {low_stock_products.count()} products ===\n"
            )
        )

        for band in low_stock_products:
            self.stdout.write(
                f"  ⚠️  {band.name} (SKU: {band.sku}) - {band.stock_quantity} left"
            )

        # Send email if requested
        if send_email:
            self._send_email_alert(low_stock_products, threshold)

        self.stdout.write(
            self.style.WARNING(
                f"\nRun with: python manage.py check_inventory --threshold={threshold}"
            )
        )

    def _send_email_alert(self, products, threshold):
        """Send email alert to administrators."""
        subject = f"SYRA Store: Low Stock Alert - {products.count()} products"

        product_list = "\n".join(
            [
                f"- {p.name} (SKU: {p.sku}): {p.stock_quantity} remaining"
                for p in products
            ]
        )

        message = (
            f"The following products have stock at or below {threshold} units:\n\n"
            f"{product_list}\n\n"
            f"Please review and restock these items promptly."
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Email alert sent to admins."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))
