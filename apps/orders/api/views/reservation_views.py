from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema

from apps.orders.api.serializers import ReservationCreateSerializer, ReservationResponseSerializer
from apps.orders.services.reservation import (
    reserve_stock, OutOfStock,
    release_reservation, confirm_reservation, InvalidReservation
)


# Create your views here.
class ReservationCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=ReservationCreateSerializer, responses=ReservationResponseSerializer)
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
                {'detail': str(e)},
                status=400
            )
        
        return Response(
            ReservationResponseSerializer(reservation).data,
            status=status.HTTP_201_CREATED
        )
    
class ReservationReleaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reservation_id):

        try:
            reservation = release_reservation(
                user=request.user, reservation_id=reservation_id
            )
        except InvalidReservation as e:
            return Response(
                {'details': str(e)},
                status=400
            )
        return Response(
            ReservationResponseSerializer(reservation).data,
            status=status.HTTP_200_OK
        )
        

class ReservationConfrimAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reservation_id):
        
        try:
            reservation = confirm_reservation(
                user=request.user, reservation_id=reservation_id
            )
        except InvalidReservation as e:
            return Response(
                {'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(
            ReservationResponseSerializer(reservation).data,
            status=status.HTTP_200_OK

        )

