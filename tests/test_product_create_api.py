import pytest


@pytest.mark.django_db
def test_create_product_with_nested_skus(client, django_user_model):
    user = django_user_model.objects.create_user(
        email="owner2@example.com", password="pass"
    )

    from apps.products.models import (
        Menu,
        Category,
        Subcategory,
        Brand,
        Product,
    )

    menu = Menu.objects.create(name="Main2", creator=user)
    category = Category.objects.create(menu=menu, name="Cat2", creator=user)
    subcat = Subcategory.objects.create(category=category, name="Sub2", creator=user)
    brand = Brand.objects.create(name="BrandY", slug="brandy", creator=user)

    payload = {
        "owner": user.id,
        "subcategory": subcat.id,
        "brand": brand.id,
        "name": "Nested Product",
        "skus": [
            {
                "sku_code": "N-SKU-1",
                "price": "29.99",
                "stock": 15,
                "attributes": {"color": "blue"},
                "images": [{"image": "sku_images/n1.jpg", "is_primary": True}],
            }
        ],
    }

    resp = client.post("/api/products/", data=payload, content_type="application/json")
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Nested Product"
    # check created nested
    product = Product.objects.get(id=data["id"])
    skus = list(product.skus.all())
    assert len(skus) == 1
    sku = skus[0]
    images = list(sku.images.all())
    assert len(images) == 1
