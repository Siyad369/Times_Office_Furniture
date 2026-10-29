from django.urls import path

from .views import (
    AdminLoginAPIView,
    AdminLogoutAPIView,
    CategoryListAPIView,
    ProductDetailAPIView,
    ProductListCreateAPIView,
)

urlpatterns = [
    path(
        "products/",
        ProductListCreateAPIView.as_view(),
        name="product-list-create",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),
    path(
        "categories/",
        CategoryListAPIView.as_view(),
        name="category-list",
    ),
    path(
        "auth/admin/login/",
        AdminLoginAPIView.as_view(),
        name="admin-login",
    ),
    path(
        "auth/admin/logout/",
        AdminLogoutAPIView.as_view(),
        name="admin-logout",
    ),
]