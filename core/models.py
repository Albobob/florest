from django.db import models
from django.core.cache import cache
from catalog.models import Category
import random

# Create your models here.

class CategoryPlaceholder(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='placeholders',
        verbose_name='Категория'
    )
    image = models.ImageField(
        upload_to='placeholders/',
        verbose_name='Изображение заглушка'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно',
        help_text='Использовать это изображение как заглушку'
    )

    class Meta:
        verbose_name = 'Заглушка категории'
        verbose_name_plural = 'Заглушки категорий'

    def __str__(self):
        return f"Заглушка для {self.category.name}"

    def save(self, *args, **kwargs):
        # Clear cache when placeholder is updated
        cache.delete(f'category_placeholders_{self.category_id}')
        super().save(*args, **kwargs)

    @classmethod
    def get_placeholder_for_category(cls, category_id):
        # Try to get placeholders from cache
        cache_key = f'category_placeholders_{category_id}'
        placeholders = cache.get(cache_key)
        
        if placeholders is None:
            # Get all active placeholders for this category
            placeholders = list(cls.objects.filter(
                category_id=category_id,
                is_active=True
            ).values_list('image', flat=True))
            
            if placeholders:
                cache.set(cache_key, placeholders)
        
        # Return random placeholder from available ones
        return random.choice(placeholders) if placeholders else None

class DefaultPlaceholder(models.Model):
    """Fallback placeholders when category has no specific placeholders"""
    image = models.ImageField(
        upload_to='placeholders/default/',
        verbose_name='Изображение заглушка'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно',
        help_text='Использовать это изображение как заглушку'
    )

    class Meta:
        verbose_name = 'Стандартная заглушка'
        verbose_name_plural = 'Стандартные заглушки'

    def save(self, *args, **kwargs):
        cache.delete('default_placeholders')
        super().save(*args, **kwargs)

    @classmethod
    def get_random_placeholder(cls):
        # Try to get from cache
        placeholders = cache.get('default_placeholders')
        
        if placeholders is None:
            # Get all active default placeholders
            placeholders = list(cls.objects.filter(
                is_active=True
            ).values_list('image', flat=True))
            
            if placeholders:
                cache.set('default_placeholders', placeholders)
        
        # Return random placeholder from available ones
        return random.choice(placeholders) if placeholders else None
