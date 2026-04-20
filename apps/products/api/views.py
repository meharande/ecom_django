from rest_framework import generics
from rest_framework.response import Response

from apps.products.models import Product
from apps.users.permissions import HasPermission
from .serializers_read import ProductSerializer
from .serializers.product import ProductCreateSerializer, ProductUpdateSerializer, ProductDeleteSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """List products (with related data) and create products."""

    queryset = Product.objects.select_related("brand", "subcategory").prefetch_related(
        "skus__images"
    )
    serializer_class = ProductSerializer
    permission_classes = [HasPermission]
    permission_resource = "product"

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductCreateSerializer
        return ProductSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        read_serializer = ProductSerializer(
            product, context=self.get_serializer_context()
        )
        return Response(read_serializer.data, status=201)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete individual products."""

    queryset = Product.objects.select_related("brand", "subcategory").prefetch_related(
        "skus__images"
    )
    serializer_class = ProductSerializer
    permission_classes = [HasPermission]
    permission_resource = "product"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ProductUpdateSerializer
        elif self.request.method == "DELETE":
            return ProductDeleteSerializer
        return ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        read_serializer = ProductSerializer(
            product, context=self.get_serializer_context()
        )
        return Response(read_serializer.data)

    def destroy(self, request, *args, **kwargs):
        # For delete, we might want to add confirmation logic
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(instance)
        return Response({"message": "Product deleted successfully"}, status=204)
