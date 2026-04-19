from rest_framework import serializers
from rest_framework.validators import ValidationError

from apps.products.models import SKU
from .sku_image import SKUImageSerializer


class SKUSerializer(serializers.ModelSerializer):
    images = SKUImageSerializer(many=True)

    class Meta:
        model = SKU
        fields = ["sku_code", "price", "stock", "attributes", "images"]

    def validate(self, attrs):
        if attrs.get("stock") < 0:
            raise ValidationError("Stock cannot be negative")
        return attrs
