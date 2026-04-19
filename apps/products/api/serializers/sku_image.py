from rest_framework import serializers

from apps.products.models import SKUImage


class SKUImageSerializer(serializers.ModelSerializer):
    # Accept image as a string (path or URL) in nested create payloads.
    image = serializers.CharField()

    class Meta:
        model = SKUImage
        fields = ["image", "is_primary"]
