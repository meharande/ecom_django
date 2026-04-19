from django.contrib import admin
from .models import (
    User,
    Role,
    Permission,
    UserPermission,
    UserRole
)

# Register your models here.
admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(UserPermission)
admin.site.register(UserRole)
from .models import Policy

admin.site.register(Policy)
