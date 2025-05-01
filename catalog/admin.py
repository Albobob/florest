from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category, Product, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ('image', 'is_preview')

@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = ("tree_actions", "indented_title", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock_status", "is_new", "is_featured", "preview_image")
    list_filter = ("category", "stock_status", "is_new", "is_featured")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ["category"]
    readonly_fields = ("created_at", "updated_at")
    inlines = [ImageInline]

    def preview_image(self, obj):
        if obj.images.filter(is_preview=True).exists():
            return obj.images.filter(is_preview=True).first().image_thumbnail.url
        return "-"
    preview_image.short_description = "Превью"

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image", "is_preview")
    list_filter = ("is_preview",)
    autocomplete_fields = ["product"]
    search_fields = ("product__name",)
