"""Custom template tags for emergency URL generation with embedded data."""

import urllib.parse
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def emergency_url(profile, request=None):
    """
    Generate emergency URL with embedded critical data.

    Usage: {% emergency_url profile %}
    Usage: {% emergency_url profile request %}

    Embeds blood type, allergies, and medications directly in URL
    for instant display even without server access.
    """
    from profiles.emergency_utils import encode_emergency_data

    # Get site base URL
    if request:
        base_url = request.build_absolute_uri("/")[:-1]  # Remove trailing slash
    else:
        base_url = "https://syra.app"  # Default production URL

    # Extract medications (first 3)
    medications = []
    if hasattr(profile, "medications"):
        for med in profile.medications.filter(is_active=True)[:3]:
            med_str = med.name
            if med.dosage:
                med_str += f" {med.dosage}"
            medications.append(med_str[:30])

    # Encode critical data
    encoded = encode_emergency_data(
        str(profile.public_id)[:8],  # Short ID
        profile.get_blood_type_display() if profile.blood_type else "Unknown",
        profile.allergies or "",
        profile.emergency_notes or "",
        medications,
    )

    # Build URL
    url = f"{base_url}/profiles/emergency/{profile.public_id}/?d={urllib.parse.quote(encoded)}"

    return mark_safe(url)


@register.simple_tag
def emergency_url_raw(profile):
    """
    Generate emergency URL without embedded data (standard URL).

    Usage: {% emergency_url_raw profile %}
    """
    return f"/profiles/emergency/{profile.public_id}/"
