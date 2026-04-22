from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.products.models import SKU

User = get_user_model()

# Create your models here.

class Reservation(models.Model):

    class Meta:
        db_table = "reservations"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)

    qty = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('CONFIRMED', 'Confirmed'),
            ('EXPIRED', 'Expired'),
            ('CANCELLED', 'Cancelled')
        ],
        default= 'ACTIVE'
    )

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() >= self.expires_at
    
    def __str__(self):
        return f"{self.user.email}-{self.sku}-{self.qty}"
    