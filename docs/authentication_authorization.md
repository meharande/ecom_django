# Authentication and Authorization Flow Documentation

## Overview

This document provides a comprehensive step-by-step explanation of the authentication and authorization system implemented in the Django e-commerce application. The system uses JWT (JSON Web Tokens) for authentication and a hybrid RBAC (Role-Based Access Control) + ABAC (Attribute-Based Access Control) approach for authorization.

## Architecture Components

### 1. Authentication Components
- **JWT Authentication**: `djangorestframework-simplejwt`
- **User Model**: Custom user model with email-based authentication
- **Token Management**: Access and refresh tokens

### 2. Authorization Components
- **HasPermission Class**: Custom permission class extending DRF's BasePermission
- **Policy Model**: Database-stored ABAC policies
- **Permission System**: Hybrid RBAC + ABAC evaluation

### 3. Key Models
- `User`: Custom user model with email-based authentication and cached permissions
- `Policy`: ABAC policy definitions stored in database with JSON conditions
- `Product`: Product model with ownership tracking
- `Permission`: Individual permission codes (RBAC)
- `Role`: Groups of permissions assignable to users

## Authentication Flow

### Step 1: User Registration/Login
```python
# apps/users/api/serializers.py - LoginSerializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["email"], password=attrs["password"])

        if not user or not user.is_active:
            raise ValidationError("User credentials did not match")

        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token), 
            "refresh": str(refresh)
        }
```

### Step 2: Token Generation
- **Access Token**: Short-lived (15 minutes) for API access
- **Refresh Token**: Long-lived (1 day) for token renewal
- Tokens contain user ID and expiration claims
- Uses HS256 signing algorithm

### User Permission Methods
```python
# apps/users/models.py
class User(AbstractBaseUser, PermissionsMixin):
    def get_permissions(self) -> set:
        """Get all permissions from roles and direct assignments with caching."""
        # Returns set of permission codes like {"product.create", "product.view"}
        
    def has_permission(self, perm_code: str) -> bool:
        """Check if user has specific permission."""
        return perm_code in self.get_permissions()
```

## Authorization Flow

### Overview
The authorization system uses a two-tier approach:
1. **RBAC**: User has explicit permissions (e.g., "product.create")
2. **ABAC**: Policies evaluate attributes (e.g., "owner.id == user.id")

### Permission Check Flow

#### Step 1: View-Level Permission Check
```python
# apps/products/api/views.py
class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [HasPermission]
    permission_resource = "product"
```

#### Step 2: HasPermission.has_permission()
```python
# apps/users/permissions.py
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
            # Defer to object-level check
            return True
        elif method == "delete":
            # Defer to object-level check
            return True

    return check_permission(request.user, resource=resource, action=action)
```

#### Step 3: check_permission() Function
```python
def check_permission(user, perm_code=None, resource=None, action=None, obj=None):
    # Step 3.1: RBAC Check
    if perm_code:
        if user and user.is_authenticated and user.has_permission(perm_code):
            return True
    else:
        if resource and action:
            code = f"{resource}.{action}"
            if user and user.is_authenticated and user.has_permission(code):
                return True

    # Step 3.2: ABAC Check
    if resource and action:
        policies = Policy.objects.filter(
            resource=resource, action=action, enabled=True
        ).order_by("priority").all()

        for policy in policies:
            conditions = policy.condition or []
            if not conditions:
                return True  # Policy with no conditions always passes

            policy_passes = True
            for rule in conditions:
                if not _eval_rule(rule, user, obj):
                    policy_passes = False
                    break

            if policy_passes:
                return True

    return False
```

#### Step 4: Object-Level Permission Check (for Update/Delete)
```python
# apps/users/permissions.py
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
            action = "view"

    return check_permission(request.user, resource=resource, action=action, obj=obj)
```

### Policy Evaluation Flow

#### Step 1: Policy Structure
```json
{
    "resource": "product",
    "action": "update",
    "condition": [
        {
            "field": "owner.id",
            "op": "eq",
            "value": "user.id"
        }
    ]
}
```

#### Step 2: Rule Evaluation (_eval_rule)
```python
def _eval_rule(rule, user, obj):
    op = rule.get("op")          # "eq"
    field = rule.get("field")    # "owner.id"
    val = rule.get("value")      # "user.id"

    # Get left side value from object
    left = _get_attr(obj, field)  # obj.owner.id

    # Get right side value
    if isinstance(val, str) and val.startswith("user."):
        right = _get_attr(user, val.replace("user.", ""))  # user.id
    else:
        right = val

    # Perform comparison
    if op == "eq":
        return left == right
```

#### Step 3: Attribute Resolution (_get_attr)
```python
def _get_attr(obj, path):
    parts = path.split(".")  # ["owner", "id"]

    cur = obj
    for p in parts:
        cur = getattr(cur, p, None)
        if cur is None:
            # Try foreign key ID field
            cur = getattr(obj, f"{p}_id", None)
            if cur is None:
                return None
    return cur
```

## Complete Request Flow Examples

### Example 1: Product Creation (Authenticated User)
1. **Client Request**: `POST /api/products/` with JWT token
2. **Authentication**: JWTAuthentication validates token, sets request.user
3. **View-Level Auth**: HasPermission.has_permission() → action="create"
4. **RBAC Check**: User has "product.create" permission → PASS
5. **Object Creation**: Product created with owner=request.user
6. **Response**: 201 Created

### Example 2: Product Update (Owner)
1. **Client Request**: `PATCH /api/products/123/` with JWT token
2. **Authentication**: JWTAuthentication validates token, sets request.user
3. **View-Level Auth**: HasPermission.has_permission() → returns True (deferred)
4. **Object Retrieval**: get_object() fetches Product instance
5. **Object-Level Auth**: HasPermission.has_object_permission() → action="update"
6. **Policy Evaluation**:
   - Policy: `owner.id == user.id`
   - _get_attr(product, "owner.id") → product.owner.id
   - _get_attr(user, "id") → user.id
   - Comparison: owner_id == user_id → PASS
7. **Update Processing**: Serializer validates and saves
8. **Response**: 200 OK

### Example 3: Product Update (Non-Owner)
1. **Client Request**: `PATCH /api/products/123/` with JWT token
2. **Authentication**: JWTAuthentication validates token, sets request.user
3. **View-Level Auth**: HasPermission.has_permission() → returns True (deferred)
4. **Object Retrieval**: get_object() fetches Product instance
5. **Object-Level Auth**: HasPermission.has_object_permission() → action="update"
6. **Policy Evaluation**:
   - Policy: `owner.id == user.id`
   - _get_attr(product, "owner.id") → product.owner.id (e.g., 456)
   - _get_attr(user, "id") → user.id (e.g., 789)
   - Comparison: 456 == 789 → FAIL
7. **Response**: 403 Forbidden

## Policy Registration

### Step 1: Policy Definition
```python
# apps/products/policies.py
DEFAULT_POLICIES = [
    {
        "resource": "product",
        "action": "update",
        "condition": [{"field": "owner.id", "op": "eq", "value": "user.id"}],
        "priority": 1,
        "enabled": True
    }
]
```

### Step 2: Policy Registration
```python
# apps/products/policies.py
def register_all():
    for policy_data in DEFAULT_POLICIES:
        Policy.objects.get_or_create(
            resource=policy_data["resource"],
            action=policy_data["action"],
            defaults=policy_data
        )
```

## Security Considerations

### 1. Token Security
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Tokens are signed with HS256 algorithm

### 2. Permission Levels
- **View**: No authentication required (public access)
- **Create**: Authenticated users only
- **Update/Delete**: Object owners only

### 3. Fallback Security
- RBAC provides basic role-based access
- ABAC provides fine-grained attribute-based control
- Policies are evaluated in priority order

## Error Handling

### Authentication Errors
- **401 Unauthorized**: Invalid or missing token
- **Token Expired**: Client must refresh token

### Authorization Errors
- **403 Forbidden**: User lacks required permissions
- Policy evaluation failures return 403

## Testing

### Permission Test Example
```python
# tests/test_products_api.py
def test_product_update_owner():
    # Create user and product
    user = User.objects.create_user(email="owner@test.com", password="pass")
    product = Product.objects.create(owner=user, ...)

    # Login and get token
    token = client.post("/api/auth/login/", {...}).json()["access"]

    # Update request
    response = client.patch(
        f"/api/products/{product.id}/",
        {"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
```

## Configuration

### Settings
```python
# config/settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

### URL Configuration
```python
# config/urls.py
urlpatterns = [
    path('api/auth/', include('apps.users.api.urls')),
    path('api/products/', include('apps.products.api.urls')),
]
```

This authentication and authorization system provides robust, scalable access control suitable for production e-commerce applications.