"""
templatetags/syra_filters.py
-----------------------------
Custom Django template filters used by SYRA templates.

Usage in templates:
  {% load syra_filters %}
  {% for item in "Diabetes, Hypertension"|split:"," %}
    {{ item|strip }}
  {% endfor %}
"""

from django import template

register = template.Library()


@register.filter(name="split")
def split_filter(value: str, delimiter: str = ",") -> list:
    """Split a string by delimiter and return a list of parts."""
    if not value:
        return []
    return value.split(delimiter)


@register.filter(name="strip")
def strip_filter(value: str) -> str:
    """Strip whitespace from a string."""
    return str(value).strip()
