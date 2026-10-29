from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "price",
        "stock_status",
        "is_active",
        "created_at",
    ]

    list_filter = [
        "category",
        "stock_status",
        "is_active",
    ]

    search_fields = [
        "title",
        "description",
    ]

    list_editable = [
        "price",
        "stock_status",
        "is_active",
    ]

    list_select_related = ["category"]
    list_per_page = 25