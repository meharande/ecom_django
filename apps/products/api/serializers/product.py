from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import ValidationError

from apps.products.models import Product, SKU, SKUImage
from .sku import SKUSerializer

User = get_user_model()


class ProductCreateSerializer(serializers.ModelSerializer):
    skus = SKUSerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False
    )

    class Meta:
        model = Product
        fields = ["owner", "subcategory", "brand", "name", "skus"]

    def validate_skus(self, value):
        if not value:
            raise ValidationError("At least one SKU is required")
        return value

    def create(self, validated_data):
        skus_data = validated_data.pop("skus", [])

        # Determine owner: prefer explicitly provided, then request user if available
        owner = validated_data.pop("owner", None)
        request = self.context.get("request")
        if (
            owner is None
            and request
            and hasattr(request, "user")
            and request.user.is_authenticated
        ):
            owner = request.user

        with transaction.atomic():
            product = Product.objects.create(
                owner=owner, creator=owner, **validated_data
            )

            for sku_data in skus_data:
                images = sku_data.pop("images", [])
                sku = SKU.objects.create(product=product, creator=owner, **sku_data)
                for img in images:
                    # img may be a dict with 'image' (path/url) and 'is_primary'
                    SKUImage.objects.create(sku=sku, creator=owner, **img)

        return product


class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating products (without nested SKUs for simplicity)."""

    class Meta:
        model = Product
        fields = ["subcategory", "brand", "name"]
        # Note: owner is not updatable for security reasons


class ProductDeleteSerializer(serializers.Serializer):
    """Serializer for delete confirmation (could include reason field if needed)."""
    confirm_delete = serializers.BooleanField(required=True)

    def validate_confirm_delete(self, value):
        if not value:
            raise ValidationError("Deletion must be confirmed")
        return value
