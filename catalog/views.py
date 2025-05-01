from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db.models import Q



class CatalogView(ListView):
    model = Product
    template_name = 'catalog/catalog.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.all()
        
        # Поиск
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Фильтрация по категории с учетом иерархии
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                # Получаем все подкатегории включая текущую
                categories = category.get_descendants(include_self=True)
                queryset = queryset.filter(category__in=categories)
            except Category.DoesNotExist:
                pass
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем категории первого уровня
        root_categories = Category.objects.filter(parent=None)
        context['root_categories'] = root_categories
        
        # Если выбрана категория, получаем её и её подкатегории
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                current_category = Category.objects.get(slug=category_slug)
                context['current_category'] = current_category
                context['subcategories'] = current_category.get_children()
                # Если это подкатегория, получаем родительскую категорию
                if current_category.parent:
                    context['parent_category'] = current_category.parent
            except Category.DoesNotExist:
                pass
        
        context['search_query'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        return context

class CategoryDetailView(ListView):
    model = Product
    template_name = 'catalog/catalog.html'
    context_object_name = 'products'

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Product.objects.filter(
            category__in=self.category.get_descendants(include_self=True)
        ).exclude(stock_status='out_of_stock')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.category
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


