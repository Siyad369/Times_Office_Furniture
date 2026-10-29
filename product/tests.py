from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Category, Product


class FurnitureCatalogTests(APITestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Office Chair"
        )

        self.product = Product.objects.create(
            title="Test Chair",
            category=self.category,
            price=Decimal("2500.00"),
        )

        user_model = get_user_model()

        self.admin = user_model.objects.create_superuser(
            username="shopadmin",
            email="admin@example.com",
            password="TestPassword123!",
        )

        self.token = Token.objects.create(user=self.admin)

    def test_category_seed_is_idempotent(self):
        call_command("seed_categories")
        call_command("seed_categories")

        self.assertEqual(
            Category.objects.filter(name="Sofa").count(),
            1,
        )

    def test_default_stock_status(self):
        self.assertEqual(
            self.product.stock_status,
            "in_stock",
        )

    def test_guest_can_list_products(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_inactive_products_are_hidden(self):
        self.product.is_active = False
        self.product.save()

        response = self.client.get("/api/products/")

        self.assertEqual(response.data["count"], 0)

    def test_category_filter(self):
        response = self.client.get(
            f"/api/products/?category={self.category.id}"
        )

        self.assertEqual(response.data["count"], 1)

    def test_search(self):
        response = self.client.get(
            "/api/products/?search=Chair"
        )

        self.assertEqual(response.data["count"], 1)

    def test_stock_filter(self):
        response = self.client.get(
            "/api/products/?stock_status=in_stock"
        )

        self.assertEqual(response.data["count"], 1)

    def test_guest_cannot_create_product(self):
        response = self.client.post(
            "/api/products/",
            {
                "title": "Unauthorized Chair",
                "category_id": self.category.id,
                "price": "1000.00",
            },
            format="json",
        )

        self.assertIn(response.status_code, [401, 403])
        self.assertFalse(
            Product.objects.filter(
                title="Unauthorized Chair"
            ).exists()
        )

    def test_admin_can_create_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.post(
            "/api/products/",
            {
                "title": "New Office Chair",
                "category_id": self.category.id,
                "price": "3500.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_admin_can_update_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.patch(
            f"/api/products/{self.product.id}/",
            {"price": "3000.00"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.price,
            Decimal("3000.00"),
        )

    def test_admin_can_delete_product(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        response = self.client.delete(
            f"/api/products/{self.product.id}/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Product.objects.filter(
                id=self.product.id
            ).exists()
        )