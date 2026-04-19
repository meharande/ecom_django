from apps.users.models import Permission, Policy


RESOURCES = [
    "menu",
    "brand",
    "category",
    "subcategory",
    "product",
    "sku",
    "sku_image",
    "permission",
    "role",
    "userrole",
    "user",
]

STANDARD_ACTIONS = ["list", "view", "create", "update", "delete"]

# Default ABAC policies (resource, action) -> condition list
DEFAULT_POLICIES = {
        ("product", "update"): [{"field": "owner", "op": "eq", "value": "user.id"}],
        ("product", "delete"): [{"field": "owner", "op": "eq", "value": "user.id"}],
        ("sku", "update"): [{"field": "product.owner", "op": "eq", "value": "user.id"}],
        ("sku", "delete"): [{"field": "product.owner", "op": "eq", "value": "user.id"}],
        ("user", "update"): [{"field": "id", "op": "eq", "value": "user.id"}],
        ("user", "delete"): [{"field": "id", "op": "eq", "value": "user.id"}],
        ("userrole", "update"): [{"field": "user.id", "op": "eq", "value": "user.id"}],
        ("userrole", "delete"): [{"field": "user.id", "op": "eq", "value": "user.id"}],
        ("permission", "update"): [{"field": "id", "op": "eq", "value": "user.id"}],
        ("permission", "delete"): [{"field": "id", "op": "eq", "value": "user.id"}],
}


def register_all(defaults_only=False):
    """Idempotently create Permission and Policy rows for all resources.

    If `defaults_only` is True, only create Policy rows that exist in
    DEFAULT_POLICIES (useful for lightweight bootstrapping).
    """
    created = {"permissions": 0, "policies": 0}

    for resource in RESOURCES:
        for action in STANDARD_ACTIONS:
            code = f"{resource}.{action}"
            desc = f"{action.capitalize()} {resource}s"
            perm, _ = Permission.objects.get_or_create(code=code, defaults={"desc": desc})
            if perm:
                created["permissions"] += 1

            # create default ABAC policy when defined
            key = (resource, action)
            if key in DEFAULT_POLICIES:
                cond = DEFAULT_POLICIES[key]
                policy, _ = Policy.objects.get_or_create(
                    resource=resource,
                    action=action,
                    defaults={"condition": cond, "priority": 100, "enabled": True},
                )
                if policy:
                    created["policies"] += 1

    return created


def register():
    """Deprecated alias kept for backwards compatibility.

    Avoid calling this at import/app-ready time because it writes to the DB.
    Prefer running the `manage_policies` management command or a data migration.
    """
    return register_all()
