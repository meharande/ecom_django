from rest_framework import generics
from rest_framework.response import Response

from apps.products.models import Product
from .serializers_read import ProductSerializer
from .serializers.product import ProductCreateSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    """List products (with related data) and create products."""

    queryset = Product.objects.select_related("brand", "subcategory").prefetch_related(
        "skus__images"
    )
    serializer_class = ProductSerializer

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
    queryset = Product.objects.select_related("brand", "subcategory").prefetch_related(
        "skus__images"
    )
    serializer_class = ProductSerializer
