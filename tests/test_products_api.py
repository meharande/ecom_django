import pytest


@pytest.mark.django_db
def test_product_list_and_detail(client, django_user_model):
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

    # list
    resp = client.get("/api/products/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict) or isinstance(data, list)

    # depending on pagination settings, data may be paginated
    results = data.get("results", data) if isinstance(data, dict) else data
    assert len(results) >= 1

    # detail
    pid = product.id
    resp2 = client.get(f"/api/products/{pid}/")
    assert resp2.status_code == 200
    d2 = resp2.json()
    assert d2["id"] == pid
    assert d2["name"] == "Prod1"
    # skus nested
    assert "skus" in d2
    assert isinstance(d2["skus"], list)
