from rest_framework import serializers

from apps.orders.models import Reservation
from apps.products.api.serializers.sku import SKUSerializer

class ReservationCreateSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField()
    qty = serializers.IntegerField(min_value=1)

class ReservationResponseSerializer(serializers.ModelSerializer):
    sku = SKUSerializer()
    class Meta:
        model = Reservation
        fields = ['id', 'sku', 'qty', 'expires_at']
    
class CartItemSerializer(serializers.ModelSerializer):

    sku_code = serializers.CharField(source='sku.sku_code')
    product_name = serializers.CharField(source='sku.product.name')

    class Meta:
        model = Reservation
        fields = [
            'id',
            'sku_id',
            'sku_code',
            'product_name',
            'qty',
            'expires_at'
        ]

class CartUpdateSerializer(serializers.Serializer):
    qty = serializers.IntegerField()
    