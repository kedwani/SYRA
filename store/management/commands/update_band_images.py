"""Management command to update band images from the media folder."""

from django.core.management.base import BaseCommand
from store.models import SyraBand


class Command(BaseCommand):
    help = "Update band images from the media folder"

    def handle(self, *args, **options):
        # Map colors to image files (relative to MEDIA_ROOT)
        image_mapping = {
            "black": "store/bracelets/main_bracelet/Matte Black band with a Brushed Silver tag.jpg",
            "red": "store/bracelets/main_bracelet/Deep Maroon band.jpg",
            "orange": "store/bracelets/main_bracelet/Bright Orange.jpg",
            "blue": "store/bracelets/main_bracelet/Navy Blue.jpg",
            "green": "store/bracelets/main_bracelet/Dark Green.jpg",
        }

        # Get all bands
        bands = SyraBand.objects.all()

        updated_count = 0
        for band in bands:
            if band.color in image_mapping:
                old_thumbnail = band.thumbnail
                band.thumbnail = image_mapping[band.color]
                band.save()
                if old_thumbnail != band.thumbnail:
                    self.stdout.write(
                        f"Updated: ID={band.id}, Color={band.color}, Image={band.thumbnail}"
                    )
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated_count} bands with images")
        )
