from rest_framework import serializers

from apps.products.models import Product
from .serializers.product import SKUSerializer


class ProductSerializer(serializers.ModelSerializer):
    skus = SKUSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "owner",
            "subcategory",
            "brand",
            "name",
            "skus",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]
