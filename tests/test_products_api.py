import pytest


@pytest.mark.django_db
def test_product_list_and_detail(client, django_user_model):
    # Register permissions and policies
    from apps.products.policies import register_all as register_products
    from apps.users.policies import register_all as register_users
    register_products()
    register_users()

    # Debug: check policies
    from apps.users.models import Policy
    policies = Policy.objects.filter(resource='product', action='update')
    print(f"Found {policies.count()} product.update policies")
    for p in policies:
        print(f"Policy: {p.condition}")

    # create user
    user = django_user_model.objects.create_user(
        email="owner@example.com", password="pass"
    )

    # create related objects (menu/category/subcategory/brand) and product
    from apps.products.models import (
        Menu,
        Category,
        Subcategory,
        Brand,
        Product,
        SKU,
        SKUImage,
    )

    menu = Menu.objects.create(
        name="Main",
        creator=user,
        creator_id=user.id,
    )
    category = Category.objects.create(menu=menu, name="Cat1", creator=user)
    subcat = Subcategory.objects.create(category=category, name="Sub1", creator=user)
    brand = Brand.objects.create(name="BrandX", slug="brandx", creator=user)

    product = Product.objects.create(
        owner=user, subcategory=subcat, brand=brand, name="Prod1", creator=user
    )

    sku = SKU.objects.create(
        product=product,
        sku_code="SKU1",
        price="9.99",
        stock=5,
        attributes={},
        creator=user,
    )
    SKUImage.objects.create(
        sku=sku, image="sku_images/test.jpg", is_primary=True, creator=user
    )

    # Login to get access token
    login_resp = client.post(
        "/api/auth/login/",
        {"email": "owner@example.com", "password": "pass"},
        content_type="application/json"
    )
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access"]

    # list
    resp = client.get(
        "/api/products/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict) or isinstance(data, list)

    # depending on pagination settings, data may be paginated
    results = data.get("results", data) if isinstance(data, dict) else data
    assert len(results) >= 1

    # detail
    pid = product.id
    resp2 = client.get(
        f"/api/products/{pid}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["id"] == pid
    assert d2["name"] == "Prod1"
    # skus nested
    assert "skus" in d2
    assert isinstance(d2["skus"], list)

    # update
    update_data = {"name": "Updated Product Name"}
    resp3 = client.patch(
        f"/api/products/{pid}/",
        data=update_data,
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp3.status_code == 200
    d3 = resp3.json()
    assert d3["name"] == "Updated Product Name"

    # delete
    resp4 = client.delete(
        f"/api/products/{pid}/",
        data={"confirm_delete": True},
        content_type="application/json",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp4.status_code == 204

    # verify deletion
    resp5 = client.get(
        f"/api/products/{pid}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert resp5.status_code == 404
