from celery import shared_task
from django.utils import timezone

from apps.orders.services.reservation import release_reservation
from apps.orders.models import Reservation

@shared_task
def expire_reservations():

    expired = (
        Reservation.objects.filter(status='ACTIVE', expires_at__lt=timezone.now())
    )

    for reservation in expired:
        try:
            release_reservation(
                reservation.user,
                reservation.id
            )
            reservation.status = 'EXPIRED'
            reservation.save()
        except Exception:
            continue