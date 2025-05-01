from django.urls import path
from .views import CatalogView, CategoryDetailView, ProductDetailView

urlpatterns = [
    path('', CatalogView.as_view(), name='catalog'),
    path('category/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
]
