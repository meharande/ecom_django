from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from apps.orders.api.serializers import (
    ReservationCreateSerializer,
    CartItemSerializer,
    CartUpdateSerializer
)
from apps.orders.services.reservation import (
    reserve_stock, OutOfStock,
    release_reservation, InvalidReservation
)
from apps.orders.models import Reservation

class AddToCartGenericView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ReservationCreateSerializer

    def post(self, request):
        
        serializer = ReservationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reservation = reserve_stock(
                user=request.user,
                sku_id=serializer.validated_data.get('sku_id'),
                qty=serializer.validated_data.get('qty') 
            )
        except OutOfStock as e:
            return Response(
                {'details': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                'reservation_id': reservation.id,
                'sku_id': reservation.sku_id,
                'qty': reservation.qty,
                'expires_at': reservation.expires_at
            },
            status=status.HTTP_201_CREATED
        )
    
class CartListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user,
            status='ACTIVE'
        ).select_related('sku', 'sku__product')
    
    def list(self, request):
        reservations = self.get_queryset()
        serializer = self.serializer_class(reservations, many=True)
        return Response(
            {'items': serializer.data},
            status=status.HTTP_200_OK
        )
    
class CartRemoveView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Reservation.objects.all()
    serializer_class = CartItemSerializer
    
    def destroy(self, request, reservation_id):
        
        try:
            reservation = Reservation.objects.get(id=reservation_id)

            reservation = release_reservation(
                user=request.user,
                reservation_id=reservation_id
            )

            
        except InvalidReservation as e:
            return Response(
                {'details': str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Reservation.DoesNotExist:
            return Response(
                {'details': 'No Item found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
                {
                    'details': "Item has been deleted",
                    'item': self.serializer_class(reservation).data
                },
                status=status.HTTP_200_OK
            )
@extend_schema(
        request= CartUpdateSerializer,
        responses= CartItemSerializer
    )   
class CartUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    
    def update(self, request, reservation_id):
        
        qty = request.data.get('qty')

        if qty <= 0:
            return Response({
                'details': 'Invalid quantity'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reservation = Reservation.objects.get(id=reservation_id)

            sku_id = reservation.sku_id

            release_reservation(request.user, reservation_id)

            new_reservation = reserve_stock(
                user=request.user,
                sku_id=sku_id,
                qty=qty
            )
        except Reservation.DoesNotExist:
            return Response(
                {'details': 'No Item found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                'item': CartItemSerializer(new_reservation).data
            },
            status=status.HTTP_202_ACCEPTED
        )
        
        