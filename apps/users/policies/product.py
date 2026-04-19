from datetime import datetime
from django.core.cache import cache


class ProductPolicy:
    def can_update(self, user, product):
        cache_key = f"policy:update:product:{product.id}:user:{user.id}"

        cached = cache.get(cache_key)
        if cache_key is not None:
            return cached

        allowed = (
            user.has_role("seller")
            and product.owner_id == user.id
            and 9 <= datetime.now().hour <= 18
        )

        cache.set(cache_key, allowed, timeout=60)  # 1 min

        return allowed
