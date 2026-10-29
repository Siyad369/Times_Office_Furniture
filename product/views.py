from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import JsonResponse

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Product
from .serializer import CategorySerializer, ProductSerializer


class ProductListCreateAPIView(APIView):
    """
    GET: Public product listing.
    POST: Admin-only product creation.
    """

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        products = Product.objects.filter(
            is_active=True
        ).select_related("category")

        category_id = request.query_params.get("category")
        search = request.query_params.get("search", "").strip()
        stock_status = request.query_params.get("stock_status")
        ordering = request.query_params.get(
            "ordering",
            "-created_at",
        )

        if category_id:
            if not category_id.isdigit():
                return Response(
                    {"error": "Category must be a valid ID."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products = products.filter(category_id=int(category_id))

        if search:
            products = products.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        if stock_status:
            valid_statuses = [
                choice[0]
                for choice in Product.STOCK_STATUS_CHOICES
            ]

            if stock_status not in valid_statuses:
                return Response(
                    {"error": "Invalid stock status."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            products = products.filter(
                stock_status=stock_status
            )

        allowed_ordering = {
            "price",
            "-price",
            "created_at",
            "-created_at",
        }

        if ordering not in allowed_ordering:
            return Response(
                {"error": "Invalid ordering value."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = products.order_by(ordering)

        from rest_framework.pagination import PageNumberPagination

        paginator = PageNumberPagination()
        paginator.page_size = 12

        page = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(page, many=True)

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()

            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProductDetailAPIView(APIView):
    """
    GET: Public product details.
    PUT/PATCH/DELETE: Admin only.
    """

    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAdminUser()]

    def get_product(self, pk):
        products = Product.objects.select_related("category")

        if self.request.method == "GET":
            products = products.filter(is_active=True)

        return products.filter(pk=pk).first()

    def get(self, request, pk):
        product = self.get_product(pk)

        if not product:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(ProductSerializer(product).data)

    def put(self, request, pk):
        product = self.get_product(pk)

        if not product:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductSerializer(
            product,
            data=request.data,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        product = self.get_product(pk)

        if not product:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        product = self.get_product(pk)

        if not product:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.delete()

        return Response(
            {"message": "Product deleted successfully."},
            status=status.HTTP_200_OK,
        )


class CategoryListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.filter(
            products__is_active=True
        ).distinct().order_by("name")

        serializer = CategorySerializer(
            categories,
            many=True,
        )

        return Response(serializer.data)


class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request=request,
            username=username,
            password=password,
        )

        if not user or not user.is_active or not user.is_staff:
            return Response(
                {"error": "Invalid admin credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Admin login successful.",
            "token": token.key,
            "username": user.username,
            "is_staff": user.is_staff,
        })


class AdminLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()

        return Response({
            "message": "Admin logged out successfully."
        })


def health_check(request):
    return JsonResponse({
        "status": "ok",
        "service": "furniture-catalog-api",
    })