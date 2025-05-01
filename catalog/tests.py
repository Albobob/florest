from django.test import TestCase
from django.urls import reverse
from .models import Category, Product, Image
from django.core.files.uploadedfile import SimpleUploadedFile

class CategoryModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", slug="test-category")

    def test_category_str(self):
        self.assertEqual(str(self.category), "Test Category")

    def test_get_absolute_url(self):
        self.assertEqual(self.category.get_absolute_url(), "/catalog/category/test-category/")

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Test Category", slug="test-category")
        self.product = Product.objects.create(
            name="Test Product",
            slug="test-product",
            category=self.category,
            short_description="Short description",
            description="Detailed description",
            price=100.00,
            in_stock=True
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product")

    def test_get_absolute_url(self):
        self.assertEqual(self.product.get_absolute_url(), "/catalog/product/test-product/")

    def test_preview_image(self):
        image = Image.objects.create(
            product=self.product,
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            is_preview=True
        )
        self.assertEqual(self.product.preview_image, image)

    def test_gallery_images(self):
        image = Image.objects.create(
            product=self.product,
            image=SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg"),
            is_preview=False
        )
        self.assertIn(image, self.product.gallery_images)

class IndexViewTests(TestCase):
    def setUp(self):
        self.outdoor = Category.objects.create(name="Outdoor", slug="outdoor")
        self.indoor = Category.objects.create(name="Indoor", slug="indoor")
        self.product1 = Product.objects.create(
            name="Outdoor Product",
            slug="outdoor-product",
            category=self.outdoor,
            short_description="Short description",
            description="Detailed description",
            price=100.00
        )
        self.product2 = Product.objects.create(
            name="Indoor Product",
            slug="indoor-product",
            category=self.indoor,
            short_description="Short description",
            description="Detailed description",
            price=200.00
        )

    def test_index_view(self):
        response = self.client.get(reverse('catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Outdoor Product")
        self.assertContains(response, "Indoor Product")