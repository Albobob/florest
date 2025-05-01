from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import CategoryPlaceholder, DefaultPlaceholder

@admin.register(CategoryPlaceholder)
class CategoryPlaceholderAdmin(admin.ModelAdmin):
    list_display = ['category', 'image_preview', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['category__name']
    list_editable = ['is_active']
    ordering = ['category', '-is_active']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px; object-fit: contain;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        # Check if there are too many active placeholders for this category
        if obj.is_active:
            active_count = CategoryPlaceholder.objects.filter(
                category=obj.category,
                is_active=True
            ).exclude(pk=obj.pk).count()
            
            if active_count >= 5:  # Limit to 5 active placeholders per category
                messages.warning(request, f'Category {obj.category} already has 5 active placeholders. Please deactivate some before adding more.')
                obj.is_active = False
        
        super().save_model(request, obj, form, change)

@admin.register(DefaultPlaceholder)
class DefaultPlaceholderAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_preview', 'is_active']
    list_filter = ['is_active']
    list_editable = ['is_active']
    ordering = ['-is_active', 'id']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px; object-fit: contain;"/>', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

    def save_model(self, request, obj, form, change):
        # Check if there are too many active default placeholders
        if obj.is_active:
            active_count = DefaultPlaceholder.objects.filter(
                is_active=True
            ).exclude(pk=obj.pk).count()
            
            if active_count >= 3:  # Limit to 3 active default placeholders
                messages.warning(request, 'There are already 3 active default placeholders. Please deactivate some before adding more.')
                obj.is_active = False
        
        super().save_model(request, obj, form, change)
