from typing import Any, Dict, List, Optional
from django.core.cache import cache
from rest_framework.permissions import BasePermission

from .models import Policy


def _get_attr(obj: Any, path: str) -> Any:
    if obj is None:
        return None
    if isinstance(obj, dict):
        parts = path.split(".")
        cur = obj
        for p in parts:
            cur = cur.get(p) if isinstance(cur, dict) else None
            if cur is None:
                return None
        return cur

    parts = path.split(".")
    cur = obj
    for p in parts:
        cur = getattr(cur, p, None)
        if cur is None:
            cur = getattr(obj, f"{p}_id", None)
            if cur is None:
                return None
    return cur


def _eval_rule(rule: Dict, user, obj) -> bool:
    op = rule.get("op")
    field = rule.get("field")
    val = rule.get("value")

    left = _get_attr(obj, field)

    # resolve right-hand side
    if isinstance(val, str) and val.startswith("user."):
        right = _get_attr(user, val.replace("user.", ""))
    else:
        right = val

    if op == "eq":
        return left == right
    if op == "neq":
        return left != right
    if op == "in":
        return left in (right or [])
    if op == "gt":
        try:
            return left > right
        except Exception:
            return False
    if op == "lt":
        try:
            return left < right
        except Exception:
            return False
    return False


def check_permission(
    user,
    perm_code: Optional[str] = None,
    resource: Optional[str] = None,
    action: Optional[str] = None,
    obj: Optional[Any] = None,
    ctx: Optional[Dict] = None,
) -> bool:
    # RBAC check (user.has_permission implemented on User model)
    if perm_code:
        if user and getattr(user, "is_authenticated", False) and user.has_permission(perm_code):
            return True
    else:
        if resource and action:
            code = f"{resource}.{action}"
            if user and getattr(user, "is_authenticated", False) and user.has_permission(code):
                return True

    # ABAC: evaluate policies for resource+action
    if resource and action:
        policies = (
            Policy.objects.filter(resource=resource, action=action, enabled=True)
            .order_by("priority")
            .all()
        )
        for p in policies:
            conds: List[Dict] = p.condition or []
            if not conds:
                return True
            ok = True
            for rule in conds:
                if not _eval_rule(rule, user, obj):
                    ok = False
                    break
            if ok:
                return True

    return False

    return False


class HasPermission(BasePermission):
    def has_permission(self, request, view):
        resource = getattr(view, "permission_resource", None) or getattr(view, "basename", None)
        action = getattr(view, "permission_action", None)
        if not action:
            method = request.method.lower()
            if method == "get":
                action = "view"
            elif method == "post":
                action = "create"
            elif method in ("put", "patch"):
                # For update, defer to object-level permission check
                return True
            elif method == "delete":
                # For delete, defer to object-level permission check
                return True
            else:
                action = method

        return check_permission(request.user, resource=resource, action=action)

    def has_object_permission(self, request, view, obj):
        resource = getattr(view, "permission_resource", None) or getattr(view, "basename", None)
        action = getattr(view, "permission_action", None)
        if not action:
            method = request.method.lower()
            if method in ("put", "patch"):
                action = "update"
            elif method == "delete":
                action = "delete"
            else:
                action = "view"  # fallback

        return check_permission(request.user, resource=resource, action=action, obj=obj)


class ProductUpdatePermission(BasePermission):
    """Compatibility wrapper for product object-level checks.

    If you prefer a per-app policy class, implement it in the app and call
    into `check_permission` or the `Policy` table.
    """

    def has_object_permission(self, request, view, obj):
        return check_permission(request.user, resource="products", action="update", obj=obj)
