from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.cache import cache

from django.db import models
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    username = models.CharField(max_length=20)
    phone = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    department = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=50, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_role(self, role_name: str) -> bool:
        cache_key = f"user:{self.id}:{role_name}"
        has_role = cache.get(cache_key)
        if has_role:
            return has_role
        roles = Role.objects.filter(
            userrole__user=self
        ).values_list("name", flat=True)

        has_role = role_name in roles

        cache.set(cache_key, has_role, timeout=300)  # Cache for 5 mins

        return has_role
    
    def get_permissions(self) -> set:
        cache_key = f"user:{self.id}:permissions"

        perms = cache.get(cache_key)

        if perms:
            return perms
        
        # Get permissions from roles
        role_perms = Permission.objects.filter(
            role__userrole__user=self
        ).values_list("code", flat=True)

        # Get direct user permissions
        user_perms = Permission.objects.filter(
            userpermission__user=self
        ).values_list("code", flat=True)

        perms = set(role_perms) | set(user_perms)

        cache.set(cache_key, perms, timeout=300)  # Cache for 5 mins

        return perms

    def has_permission(self, perm_code: str) -> bool:
        return perm_code in self.get_permissions()

class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    desc = models.CharField(max_length=255)

    class Meta:
        db_table = "permissions"

    def __str__(self):
        return self.code
    
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "role"]
        db_table = "user_roles"

    def __str__(self):
        return f"{self.user.email} -> {self.role.name}"

class UserPermission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user", "permission"]
        db_table = "user_permissions"

class Policy(models.Model):
    """Simple ABAC policy store.

    `condition` is a list of simple rule dicts of the form:
      {"field": "owner", "op": "eq", "value": "user.id"}

    We intentionally keep the expression language tiny to avoid eval.
    """

    resource = models.CharField(max_length=100)
    action = models.CharField(max_length=50)
    condition = models.JSONField(blank=True, null=True)
    priority = models.IntegerField(default=100)
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ["resource", "action", "priority"]
        db_table = "policies"

    def __str__(self):
        return f"{self.resource}:{self.action} (p={self.priority})"


