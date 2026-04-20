# Version 1

## Project Overview

This document captures the initial implementation of the e-commerce application, focusing on authentication, authorization, product APIs, and management command setup.

## Apps

- `apps.users`
  - Custom `User` model with email-based login
  - Role and permission models for RBAC
  - Policy model for ABAC
  - Login API serializer and view
  - Authorization engine for view-level and object-level checks

- `apps.products`
  - Product, SKU, SKUImage models
  - Product API views and serializers
  - Product-specific policies for ownership-based access

- `apps.core`
  - Management commands moved here
  - `manage_policies` and `seed_demo`

## Authentication

- Uses `rest_framework_simplejwt`
- JWT-based authentication with access and refresh tokens
- Configured in `config/settings/base.py`
- Login serializer authenticates using email and password
- Tokens returned as `access` and `refresh`

## Authorization

### RBAC
- `Permission`, `Role`, `UserRole`, and `UserPermission` models
- `User.get_permissions()` aggregates role and direct permissions
- `User.has_permission(code)` checks permission membership

### ABAC
- `Policy` model stores `resource`, `action`, `condition`, `priority`, and `enabled`
- Conditions are JSON rule lists like `{"field": "owner.id", "op": "eq", "value": "user.id"}`
- `apps/users/permissions.py` contains the ABAC engine

### Permission evaluation
- `HasPermission.has_permission()` handles view-level checks
- `HasPermission.has_object_permission()` handles object-level checks for update/delete
- `check_permission()` performs RBAC first, then ABAC
- `_get_attr()` resolves nested field paths
- `_eval_rule()` evaluates operators like `eq`, `neq`, `in`, `gt`, `lt`

## Product API

- `ProductListCreateView` and `ProductDetailView` in `apps/products/api/views.py`
- Uses `HasPermission` for authorization
- `permission_resource = "product"`
- Product update/delete require owner-based policy checks

## Policy registration

- `apps/users/policies.py` and `apps/products/policies.py` define default policies
- `register_all()` creates permissions and policies in the database
- `manage_policies` command bootstraps these records

## Key fixes made

- Moved `management/commands` into `apps/core/management/commands`
- Added `apps.core` to `INSTALLED_APPS`
- Fixed `SIMPLE_JWT["AUTH_TOKEN_CLASSES"]` to be a tuple
- Ensured object-level permission checks receive the real object

## Testing

- Existing tests verify login, product creation, product list/detail, and product update/delete behavior
- `pytest tests/ -v` passes successfully

## Notes

This is the initial implementation version capturing the current state of authentication, authorization, and policy flows. Future versions can extend this with additional API resources, policy types, and stronger role management.
