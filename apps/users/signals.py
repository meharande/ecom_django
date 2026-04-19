from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.users.models import UserRole


@receiver([post_save, post_delete], sender=UserRole)
def clear_user_role_cache(sender, instance, **kwargs):
    cache_key = f"user:{instance.user_id}:roles"
    cache.delete(cache_key)
