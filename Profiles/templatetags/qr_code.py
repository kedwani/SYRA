"""Custom template tags for QR code generation."""

import base64
import io

import qrcode
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def qr_code(data, size=200):
    """
    Generate a local QR code and return as base64 data URL.

    Usage: {{ profile.public_id|qr_code }}
    Or with size: {{ profile.public_id|qr_code:300 }}
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Resize to requested size
    img = img.resize((size, size))

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return mark_safe(f"data:image/png;base64,{img_str}")
