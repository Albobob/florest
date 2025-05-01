from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit
from django.urls import reverse
from meta.models import ModelMeta

class Category(MPTTModel):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-имя")
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                            verbose_name="Родительская категория")

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

class Product(ModelMeta, models.Model):
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'В наличии'),
        ('on_order', 'Под заказ'),
        ('out_of_stock', 'Нет в наличии'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-имя")
    category = TreeForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    short_description = models.TextField(max_length=500, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Подробное описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    height = models.CharField(max_length=100, verbose_name="Высота", blank=True)
    flowering = models.CharField(max_length=100, verbose_name="Цветение", blank=True)
    planting_conditions = models.TextField(verbose_name="Условия посадки", blank=True)

    stock_status = models.CharField(
        max_length=20,
        choices=STOCK_STATUS_CHOICES,
        default='in_stock',
        verbose_name="Статус наличия"
    )
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_featured = models.BooleanField(default=False, verbose_name="Показать на главной")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    _metadata = {
        'title': 'name',
        'description': 'short_description',
    }

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    @property
    def in_stock(self):
        """Compatibility property for existing code"""
        return self.stock_status == 'in_stock'

    @property
    def preview_image(self):
        """Возвращает превью изображение товара"""
        preview = self.images.filter(is_preview=True).first()
        if preview:
            return preview.image
        return self.images.first().image if self.images.exists() else None

    @property
    def preview_image_url(self):
        """Возвращает URL превью изображения товара"""
        preview = self.images.filter(is_preview=True).first()
        if preview:
            return preview.image_thumbnail.url
        return self.images.first().image_thumbnail.url if self.images.exists() else None

    @property
    def gallery_images(self):
        """Возвращает все изображения для галереи (не превью)"""
        return self.images.filter(is_preview=False)

class Image(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/%Y/%m/%d', verbose_name="Изображение")
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFit(300, 300)],
        format='JPEG',
        options={'quality': 85}
    )
    is_preview = models.BooleanField(default=False, verbose_name="Использовать как превью")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ['-is_preview', 'id']

    def __str__(self):
        return f"{'Превью' if self.is_preview else 'Галерея'} для {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_preview:
            # Если это превью, убираем флаг превью у других изображений этого товара
            Image.objects.filter(product=self.product, is_preview=True).update(is_preview=False)
        super().save(*args, **kwargs)