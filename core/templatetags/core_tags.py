from django import template
from core.models import CategoryPlaceholder, DefaultPlaceholder
from django.conf import settings
from django.templatetags.static import static

register = template.Library()

@register.simple_tag
def get_placeholder_image(category_id=None):
    """
    Returns a placeholder image URL based on the following priority:
    1. Category-specific placeholder (random if multiple exist)
    2. Default placeholder (random if multiple exist)
    3. Static fallback image
    """
    if category_id:
        # Try to get category-specific placeholder
        category_placeholder = CategoryPlaceholder.get_placeholder_for_category(category_id)
        if category_placeholder:
            return f"{settings.MEDIA_URL}{category_placeholder}"

    # Fallback to default placeholder
    default_placeholder = DefaultPlaceholder.get_random_placeholder()
    if default_placeholder:
        return f"{settings.MEDIA_URL}{default_placeholder}"
    
    # Final fallback to static image
    return static('images/placeholder.jpg') 