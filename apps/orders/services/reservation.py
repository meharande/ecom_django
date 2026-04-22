from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from apps.products.models import SKU
from apps.orders.models import Reservation

RESERVATION_TTL_MINUTES = 10

class OutOfStock(Exception):
    pass

class InvalidReservation(Exception):
    pass

def reserve_stock(user, sku_id, qty):
    with transaction.atomic():
        # Lock the row
        sku = SKU.objects.select_for_update().get(id=sku_id)

        available = sku.stock - sku.reserved_stock

        if qty > available:
            raise OutOfStock('Insufficient stock')
        
        # Reserve
        sku.reserved_stock += qty
        sku.save()
        
        reservation = Reservation.objects.create(
            user=user,
            sku=sku,
            qty=qty,
            expires_at = timezone.now() + timedelta(minutes=RESERVATION_TTL_MINUTES),
        )

        return reservation

@transaction.atomic   
def release_reservation(user, reservation_id):
    
    reservation = (
        Reservation.objects.select_for_update()
        .select_related('sku')
        .get(id=reservation_id)
    )

    if reservation.user_id != user.id:
        raise InvalidReservation('Not allowed')

    if reservation.status != 'ACTIVE':
        raise InvalidReservation('Reservation is not active')
    
    sku = (
        reservation.sku.__class__.objects
        .select_for_update()
        .get(id=reservation.sku_id)
    )

    # remove reservation stock
    sku.reserved_stock -= reservation.qty

    if sku.reserved_stock < 0:
        sku.reserved_stock = 0 # Safty guard

    sku.save()

    # mark reservation is Cancelled
    reservation.status = 'CANCELLED'
    reservation.save()

    return reservation


@transaction.atomic
def confirm_reservation(user, reservation_id):
    
    reservation = (
        Reservation.objects.select_for_update()
        .select_related('sku')
        .get(id=reservation_id)
    )

    if reservation.user_id != user.id:
        raise InvalidReservation('Not allowed')
    
    if reservation.status != 'ACTIVE':
        raise InvalidReservation('Reservation is not active')
    
    sku = (
        reservation.sku.__class__.objects
        .select_for_update()
        .get(id=reservation.sku_id)
    )

    sku.stock -= reservation.qty
    sku.reserved_stock -= reservation.qty

    if sku.stock < 0:
        raise InvalidReservation('Stock mismatch')
    
    sku.save()

    reservation.status = 'CONFIRM'
    reservation.save()

    return reservation
