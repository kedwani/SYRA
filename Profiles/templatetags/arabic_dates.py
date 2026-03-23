"""Custom template tags for culturally appropriate date formatting."""

from django import template
from django.utils import translation
from django.utils.formats import get_format

register = template.Library()


@register.filter
def localized_date(date, format_type="medium"):
    """
    Format date based on current language.

    Usage: {{ profile.updated_at|localized_date }}
           {{ profile.updated_at|localized_date:'short' }}
           {{ profile.updated_at|localized_date:'full' }}

    Args:
        date: A datetime object or None
        format_type: 'short', 'medium', or 'full'

    Returns:
        Formatted date string in Arabic (DD/MM/YYYY) or English (M d, Y)
    """
    if not date:
        return ""

    lang = translation.get_language() or "en"

    # Arabic users prefer DD/MM/YYYY format
    if lang.startswith("ar"):
        if format_type == "short":
            return date.strftime("%d/%m/%Y")
        elif format_type == "full":
            return date.strftime("%d %B %Y")
        else:  # medium (default)
            return date.strftime("%d/%m/%Y")
    else:
        # English users get M d, Y format (using Django's date format)
        if format_type == "short":
            return date.strftime("%m/%d/%Y")
        elif format_type == "full":
            return date.strftime("%B %d, %Y")
        else:  # medium (default)
            return date.strftime("%b %d, %Y")


@register.filter
def localized_datetime(date, format_type="medium"):
    """
    Format datetime based on current language.

    Usage: {{ order.created_at|localized_datetime }}
           {{ order.created_at|localized_datetime:'full' }}
    """
    if not date:
        return ""

    lang = translation.get_language() or "en"

    if lang.startswith("ar"):
        if format_type == "short":
            return date.strftime("%d/%m/%Y %H:%M")
        elif format_type == "full":
            return date.strftime("%d %B %Y %H:%M")
        else:  # medium
            return date.strftime("%d/%m/%Y %H:%M")
    else:
        if format_type == "short":
            return date.strftime("%m/%d/%Y %H:%M")
        elif format_type == "full":
            return date.strftime("%B %d, %Y %H:%M")
        else:  # medium
            return date.strftime("%b %d, %Y %H:%M")


@register.simple_tag
def hijri_date(gregorian_date):
    """
    Convert and display Gregorian date in Hijri calendar.

    Usage: {% hijri_date profile.updated_at %}

    Requires: pip install hijri-converter

    Returns:
        String in format: "15 Ramadan 1446هـ"
    """
    if not gregorian_date:
        return ""

    try:
        from hijri_converter import convert

        hijri = convert.Gregorian(
            gregorian_date.year, gregorian_date.month, gregorian_date.day
        ).to_hijri()

        return f"{hijri.day} {hijri.month_name()} {hijri.year}هـ"
    except ImportError:
        # Fallback if hijri-converter is not installed
        return localized_date(gregorian_date)
    except Exception:
        # Fallback for any conversion errors
        return localized_date(gregorian_date)


@register.filter
def localized_date_input(date):
    """
    Format date for input fields (always YYYY-MM-DD for HTML5 date inputs).

    Usage: {{ user.date_of_birth|localized_date_input }}
    """
    if not date:
        return ""

    return date.strftime("%Y-%m-%d")
