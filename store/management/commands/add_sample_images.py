"""
Management command to add sample images to SyraBand products.
Uses placeholder service for demo images.
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from store.models import SyraBand
import requests
from io import BytesIO


class Command(BaseCommand):
    help = "Add sample images to existing SyraBand products"

    # Placeholder image URLs for different band colors
    PLACEHOLDER_IMAGES = {
        "black": "https://placehold.co/400x400/1f2937/ffffff?text=SYRA+Black",
        "white": "https://placehold.co/400x400/f3f4f6/1f2937?text=SYRA+White",
        "blue": "https://placehold.co/400x400/3b82f6/ffffff?text=SYRA+Blue",
        "red": "https://placehold.co/400x400/ef4444/ffffff?text=SYRA+Red",
        "green": "https://placehold.co/400x400/22c55e/ffffff?text=SYRA+Green",
        "pink": "https://placehold.co/400x400/ec4899/ffffff?text=SYRA+Pink",
        "orange": "https://placehold.co/400x400/f97316/ffffff?text=SYRA+Orange",
        "purple": "https://placehold.co/400x400/a855f7/ffffff?text=SYRA+Purple",
    }

    def handle(self, *args, **options):
        bands = SyraBand.objects.all()

        if not bands.exists():
            self.stdout.write(
                self.style.WARNING("No products found. Run seed_products first.")
            )
            return

        self.stdout.write(f"Adding sample images to {bands.count()} products...")

        for band in bands:
            color = band.color.lower()
            image_url = self.PLACEHOLDER_IMAGES.get(
                color, self.PLACEHOLDER_IMAGES["black"]
            )

            try:
                # Download image from placeholder service
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    image_content = response.content
                    filename = f"{band.sku.lower()}.png"

                    # Save to thumbnail field
                    band.thumbnail.save(filename, ContentFile(image_content), save=True)

                    self.stdout.write(self.style.SUCCESS(f"Added image to {band.name}"))
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Failed to download image for {band.name}")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error adding image to {band.name}: {str(e)}")
                )

        self.stdout.write(self.style.SUCCESS("Done adding sample images!"))
